"""
Application Layer - Dang Ky Lop Hoc Phan Use Case
"""
from core.types import ServiceResult
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository,
    ILichHocDinhKyRepository
)
from application.enrollment.interfaces import (
    IKyPhaseRepository,
    IGhiDanhRepository,
    IHocPhanRepository
)
from django.db import transaction

class DangKyLopHocPhanUseCase:
    """
    Use case to register for a course class (Lop Hoc Phan)
    """
    
    def __init__(
        self,
        ky_phase_repo: IKyPhaseRepository,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        ghi_danh_repo: IGhiDanhRepository,
        hoc_phan_repo: IHocPhanRepository,
        dang_ky_hp_repo: IDangKyHocPhanRepository,
        dang_ky_tkb_repo: IDangKyTKBRepository,
        lich_su_repo: ILichSuDangKyRepository,
        lich_hoc_repo: ILichHocDinhKyRepository
    ):
        self.ky_phase_repo = ky_phase_repo
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.ghi_danh_repo = ghi_danh_repo
        self.hoc_phan_repo = hoc_phan_repo
        self.dang_ky_hp_repo = dang_ky_hp_repo
        self.dang_ky_tkb_repo = dang_ky_tkb_repo
        self.lich_su_repo = lich_su_repo
        self.lich_hoc_repo = lich_hoc_repo

    def execute(self, request_data: dict, user_id: str) -> ServiceResult:
        """
        Execute registration logic
        """
        lop_hoc_phan_id = request_data.get('lopHocPhanId')
        hoc_ky_id = request_data.get('hocKyId')
        
        if not lop_hoc_phan_id or not hoc_ky_id:
            return ServiceResult.fail("Thiếu thông tin lớp học phần hoặc học kỳ", error_code="INVALID_INPUT")

        # 1. Check Phase
        phase = self.ky_phase_repo.get_current_phase(hoc_ky_id)
        if not phase or phase.phase != "dang_ky_hoc_phan":
            return ServiceResult.fail("Chưa đến giai đoạn đăng ký học phần hoặc phase đã đóng", error_code="PHASE_NOT_OPEN")

        # 2. Check Lop Hoc Phan
        lop_hoc_phan = self.lop_hoc_phan_repo.find_by_id(lop_hoc_phan_id)
        if not lop_hoc_phan:
            return ServiceResult.fail("Lớp học phần không tồn tại", error_code="LHP_NOT_FOUND")

        # 3. Check Ghi Danh
        is_ghi_danh = self.ghi_danh_repo.is_already_registered(user_id, str(lop_hoc_phan.hoc_phan_id))
        if not is_ghi_danh:
            return ServiceResult.fail("Bạn phải ghi danh học phần này trước khi đăng ký lớp", error_code="NOT_GHI_DANH")

        # 4. Check Duplicate Mon Hoc
        hoc_phan = self.hoc_phan_repo.find_by_id(str(lop_hoc_phan.hoc_phan_id))
        if not hoc_phan:
            return ServiceResult.fail("Học phần không tồn tại", error_code="HOC_PHAN_NOT_FOUND")
            
        has_registered_mon = self.dang_ky_hp_repo.has_registered_mon_hoc_in_hoc_ky(
            user_id, 
            str(hoc_phan.mon_hoc_id), 
            hoc_ky_id
        )
        if has_registered_mon:
            return ServiceResult.fail("Bạn đã đăng ký một lớp khác của cùng môn trong học kỳ này", error_code="ALREADY_REGISTERED_MON_HOC")

        # 5. Check Slot
        so_luong_hien_tai = lop_hoc_phan.so_luong_hien_tai or 0
        so_luong_toi_da = lop_hoc_phan.so_luong_toi_da or 50
        if so_luong_hien_tai >= so_luong_toi_da:
            return ServiceResult.fail("Lớp học phần đã đầy", error_code="LHP_FULL")

        # 6. Check Already Registered Class
        already_registered = self.dang_ky_hp_repo.is_student_registered(user_id, lop_hoc_phan_id)
        if already_registered:
            return ServiceResult.fail("Bạn đã đăng ký lớp học phần này rồi", error_code="ALREADY_REGISTERED")

        # 7. Check TKB Conflict
        conflict_result = self._check_tkb_conflict(user_id, lop_hoc_phan_id, hoc_ky_id)
        if not conflict_result.success:
            return conflict_result

        # 8. Transaction
        try:
            with transaction.atomic():
                # 8.1 Create Dang Ky Hoc Phan
                dang_ky = self.dang_ky_hp_repo.create({
                    'sinh_vien_id': user_id,
                    'lop_hoc_phan_id': lop_hoc_phan_id,
                    'trang_thai': 'da_dang_ky',
                    'co_xung_dot': False
                })
                
                # 8.2 Log History
                self.lich_su_repo.upsert_and_log(
                    user_id, 
                    hoc_ky_id, 
                    str(dang_ky.id), 
                    "dang_ky"
                )
                
                # 8.3 Create Dang Ky TKB
                self.dang_ky_tkb_repo.create({
                    'dang_ky_id': str(dang_ky.id),
                    'sinh_vien_id': user_id,
                    'lop_hoc_phan_id': lop_hoc_phan_id
                })
                
                # 8.4 Update Slot
                self.lop_hoc_phan_repo.update_so_luong(lop_hoc_phan_id, 1)
                
            return ServiceResult.ok(None, "Đăng ký học phần thành công")
            
        except Exception as e:
            print(f"Error registering course: {e}")
            return ServiceResult.fail("Lỗi khi đăng ký học phần", error_code="INTERNAL_ERROR")

    def _check_tkb_conflict(self, user_id: str, new_lhp_id: str, hoc_ky_id: str) -> ServiceResult:
        # Get existing schedule
        registered_lhps = self.dang_ky_tkb_repo.find_registered_lop_hoc_phans_by_hoc_ky(user_id, hoc_ky_id)
        
        # Get new class schedule
        new_lich_hocs = self.lich_hoc_repo.find_by_lop_hoc_phan(new_lhp_id)
        if not new_lich_hocs:
            return ServiceResult.ok(None) # No schedule, no conflict
            
        for reg in registered_lhps:
            # Assuming reg is DangKyTKB object with lop_hoc_phan relation
            existing_lhp = reg.lop_hoc_phan
            existing_lich_hocs = self.lich_hoc_repo.find_by_lop_hoc_phan(str(existing_lhp.id))
            
            for exist_lh in existing_lich_hocs:
                for new_lh in new_lich_hocs:
                    if exist_lh.thu == new_lh.thu:
                        if self._is_time_overlap(
                            exist_lh.tiet_bat_dau, exist_lh.tiet_ket_thuc,
                            new_lh.tiet_bat_dau, new_lh.tiet_ket_thuc
                        ):
                            return ServiceResult.fail(
                                f"Xung đột lịch học với môn {existing_lhp.hoc_phan.ten_hoc_phan} - Lớp {existing_lhp.ma_lop}",
                                error_code="TKB_CONFLICT"
                            )
        return ServiceResult.ok(None)

    def _is_time_overlap(self, start1: int, end1: int, start2: int, end2: int) -> bool:
        return max(start1, start2) <= min(end1, end2)
