"""
Application Layer - Chuyen Lop Hoc Phan Use Case
"""
from core.types import ServiceResult
from application.course_registration.interfaces import (
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository,
    ILopHocPhanRepository,
    ILichHocDinhKyRepository
)
from application.enrollment.interfaces import IHocPhanRepository
from django.db import transaction

class ChuyenLopHocPhanUseCase:
    """
    Use case to switch course class
    """
    
    def __init__(
        self,
        dang_ky_hp_repo: IDangKyHocPhanRepository,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        hoc_phan_repo: IHocPhanRepository,
        dang_ky_tkb_repo: IDangKyTKBRepository,
        lich_su_repo: ILichSuDangKyRepository,
        lich_hoc_repo: ILichHocDinhKyRepository
    ):
        self.dang_ky_hp_repo = dang_ky_hp_repo
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.hoc_phan_repo = hoc_phan_repo
        self.dang_ky_tkb_repo = dang_ky_tkb_repo
        self.lich_su_repo = lich_su_repo
        self.lich_hoc_repo = lich_hoc_repo

    def execute(self, request_data: dict, user_id: str) -> ServiceResult:
        """
        Execute switch logic
        """
        lop_hoc_phan_id_cu = request_data.get('lopHocPhanIdCu')
        lop_hoc_phan_id_moi = request_data.get('lopHocPhanIdMoi')
        
        if not lop_hoc_phan_id_cu or not lop_hoc_phan_id_moi:
            return ServiceResult.fail("Thiếu ID lớp cũ hoặc lớp mới", error_code="INVALID_INPUT")
            
        if lop_hoc_phan_id_cu == lop_hoc_phan_id_moi:
            return ServiceResult.fail("Lớp cũ và lớp mới không được trùng nhau", error_code="SAME_CLASS")

        # 1. Check Old Dang Ky
        dang_ky_cu = self.dang_ky_hp_repo.find_by_sinh_vien_and_lop_hoc_phan(user_id, lop_hoc_phan_id_cu)
        if not dang_ky_cu:
            return ServiceResult.fail("Không tìm thấy record đăng ký lớp cũ", error_code="OLD_CLASS_NOT_FOUND")
            
        if dang_ky_cu.trang_thai != "da_dang_ky":
            return ServiceResult.fail("Lớp cũ đã bị hủy, không thể chuyển", error_code="OLD_CLASS_CANCELLED")

        # 2. Check New Class
        lop_moi = self.lop_hoc_phan_repo.find_by_id(lop_hoc_phan_id_moi)
        if not lop_moi:
            return ServiceResult.fail("Lớp mới không tồn tại", error_code="NEW_CLASS_NOT_FOUND")

        # 3. Check Same Subject
        hoc_phan_cu = dang_ky_cu.lop_hoc_phan.hoc_phan
        hoc_phan_moi = self.hoc_phan_repo.find_by_id(str(lop_moi.hoc_phan_id))
        
        if not hoc_phan_moi or str(hoc_phan_cu.mon_hoc_id) != str(hoc_phan_moi.mon_hoc_id):
            return ServiceResult.fail("Lớp mới không cùng môn học với lớp cũ", error_code="DIFFERENT_SUBJECT")

        # 4. Check Slot
        so_luong_hien_tai = lop_moi.so_luong_hien_tai or 0
        so_luong_toi_da = lop_moi.so_luong_toi_da or 50
        if so_luong_hien_tai >= so_luong_toi_da:
            return ServiceResult.fail("Lớp mới đã đầy", error_code="NEW_CLASS_FULL")

        # 5. Check TKB Conflict
        hoc_ky_id = str(hoc_phan_moi.id_hoc_ky)
        conflict_result = self._check_tkb_conflict(user_id, lop_hoc_phan_id_cu, lop_hoc_phan_id_moi, hoc_ky_id)
        if not conflict_result.success:
            return conflict_result

        # 6. Transaction
        try:
            with transaction.atomic():
                # 6.1 Update Dang Ky
                self.dang_ky_hp_repo.update_lop_hoc_phan(str(dang_ky_cu.id), lop_hoc_phan_id_moi)
                
                # 6.2 Update Dang Ky TKB
                self.dang_ky_tkb_repo.update_lop_hoc_phan(str(dang_ky_cu.id), lop_hoc_phan_id_moi)
                
                # 6.3 Log History
                self.lich_su_repo.upsert_and_log(
                    user_id,
                    hoc_ky_id,
                    str(dang_ky_cu.id),
                    "dang_ky" # Action remains 'dang_ky' as per legacy logic, or maybe 'chuyen_lop'? Legacy says 'dang_ky'
                )
                
                # 6.4 Update Slots
                self.lop_hoc_phan_repo.update_so_luong(lop_hoc_phan_id_cu, -1)
                self.lop_hoc_phan_repo.update_so_luong(lop_hoc_phan_id_moi, 1)
                
            return ServiceResult.ok(None, "Chuyển lớp học phần thành công")
            
        except Exception as e:
            print(f"Error switching class: {e}")
            return ServiceResult.fail("Lỗi khi chuyển lớp học phần", error_code="INTERNAL_ERROR")

    def _check_tkb_conflict(self, user_id: str, old_lhp_id: str, new_lhp_id: str, hoc_ky_id: str) -> ServiceResult:
        # Get registered classes excluding old class
        registered_lhps = self.dang_ky_tkb_repo.find_registered_lop_hoc_phans_by_hoc_ky(user_id, hoc_ky_id)
        filtered_lhps = [r for r in registered_lhps if str(r.lop_hoc_phan.id) != old_lhp_id]
        
        # Get new class schedule
        new_lich_hocs = self.lich_hoc_repo.find_by_lop_hoc_phan(new_lhp_id)
        if not new_lich_hocs:
            return ServiceResult.ok(None)
            
        for reg in filtered_lhps:
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
