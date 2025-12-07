"""
Application Layer - Chuyen Lop Hoc Phan Use Case
"""
from typing import List, Any, Optional
from core.types import ServiceResult
from django.db import transaction
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository
)
from infrastructure.persistence.enrollment.repositories import KyPhaseRepository
from infrastructure.persistence.sinh_vien.sinh_vien_repository import SinhVienRepository
from infrastructure.persistence.common.repositories import HocKyRepository

class ChuyenLopHocPhanUseCase:
    """
    Use case to transfer course class (Chuyen Lop)
    """
    
    def __init__(
        self,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        dang_ky_hp_repo: IDangKyHocPhanRepository,
        dang_ky_tkb_repo: IDangKyTKBRepository,
        lich_su_repo: ILichSuDangKyRepository,
        ky_phase_repo: KyPhaseRepository,
        sinh_vien_repo: SinhVienRepository,
        hoc_ky_repo: HocKyRepository = None
    ):
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.dang_ky_hp_repo = dang_ky_hp_repo
        self.dang_ky_tkb_repo = dang_ky_tkb_repo
        self.lich_su_repo = lich_su_repo
        self.ky_phase_repo = ky_phase_repo
        self.sinh_vien_repo = sinh_vien_repo
        self.hoc_ky_repo = hoc_ky_repo or HocKyRepository()
        
    def execute(self, sinh_vien_id: str, lop_cu_id: str, lop_moi_id: str, hoc_ky_id: Optional[str] = None) -> ServiceResult:
        """
        Execute transfer logic
        If hoc_ky_id not provided, will get from hoc_ky_hien_hanh
        """
        try:
            # 1. Validate Student
            sinh_vien = self.sinh_vien_repo.get_by_id(sinh_vien_id)
            if not sinh_vien:
                return ServiceResult.fail("Sinh viên không tồn tại", error_code="STUDENT_NOT_FOUND")

            # 2. Get hoc_ky_id if not provided
            if not hoc_ky_id:
                hoc_ky = self.hoc_ky_repo.find_hien_hanh()
                if not hoc_ky:
                    return ServiceResult.fail("Không tìm thấy học kỳ hiện hành", error_code="HOC_KY_NOT_FOUND")
                hoc_ky_id = str(hoc_ky.id)

            # 3. Check Phase
            current_phase = self.ky_phase_repo.get_current_phase(hoc_ky_id)
            if not current_phase or current_phase.phase != "dang_ky_hoc_phan":
                return ServiceResult.fail(
                    "Không trong thời gian đăng ký học phần", 
                    error_code="INVALID_PHASE"
                )

            # 3. Validate Old Registration
            dang_ky_cu = self.dang_ky_hp_repo.find_by_sinh_vien_and_lop_hoc_phan(sinh_vien_id, lop_cu_id)
            if not dang_ky_cu:
                return ServiceResult.fail("Chưa đăng ký lớp học phần cũ", error_code="OLD_REGISTRATION_NOT_FOUND")
            
            if dang_ky_cu.trang_thai != "da_dang_ky":
                return ServiceResult.fail("Trạng thái lớp cũ không hợp lệ", error_code="INVALID_OLD_STATUS")

            # 4. Validate New Class
            lop_moi = self.lop_hoc_phan_repo.find_by_id(lop_moi_id)
            if not lop_moi:
                return ServiceResult.fail("Lớp học phần mới không tồn tại", error_code="NEW_CLASS_NOT_FOUND")
            
            # Check Quantity
            if (lop_moi.so_luong_hien_tai or 0) >= (lop_moi.so_luong_toi_da or 50):
                return ServiceResult.fail("Lớp học phần mới đã đầy", error_code="NEW_CLASS_FULL")

            # 5. Check Subject Match
            # Need to fetch old class info to check subject
            lop_cu = self.lop_hoc_phan_repo.find_by_id(lop_cu_id) # Should exist if registration exists, but safe to check
            if not lop_cu:
                 return ServiceResult.fail("Lớp học phần cũ không tồn tại (dữ liệu lỗi)", error_code="OLD_CLASS_NOT_FOUND")
                 
            if lop_cu.hoc_phan.mon_hoc_id != lop_moi.hoc_phan.mon_hoc_id:
                return ServiceResult.fail("Lớp mới không thuộc cùng môn học với lớp cũ", error_code="SUBJECT_MISMATCH")

            # 6. Check Time Conflict (Excluding Old Class)
            new_schedules = list(lop_moi.lichhocdinhky_set.all())
            
            # Get all registered classes
            existing_registrations = self.dang_ky_tkb_repo.find_registered_lop_hoc_phans_by_hoc_ky(sinh_vien_id, hoc_ky_id)
            
            for reg in existing_registrations:
                # Skip the old class we are moving away from
                if str(reg.lop_hoc_phan.id) == lop_cu_id:
                    continue
                    
                existing_lhp = reg.lop_hoc_phan
                existing_schedules = existing_lhp.lichhocdinhky_set.all()
                
                if self._check_conflict(new_schedules, existing_schedules):
                    return ServiceResult.fail(
                        f"Trùng lịch học với lớp {existing_lhp.ma_lop}", 
                        error_code="TIME_CONFLICT"
                    )

            # 7. Atomic Transaction
            with transaction.atomic(using='neon'):
                # A. Cancel Old
                self.dang_ky_tkb_repo.delete_by_dang_ky_id(str(dang_ky_cu.id))
                self.dang_ky_hp_repo.update_status(str(dang_ky_cu.id), "da_huy")
                self.lop_hoc_phan_repo.update_so_luong(lop_cu_id, -1)
                
                # B. Register New
                dang_ky_moi = self.dang_ky_hp_repo.create({
                    "sinh_vien_id": sinh_vien_id,
                    "lop_hoc_phan_id": lop_moi_id,
                    "trang_thai": "da_dang_ky"
                })
                
                self.dang_ky_tkb_repo.create({
                    "dang_ky_id": dang_ky_moi.id,
                    "sinh_vien_id": sinh_vien_id,
                    "lop_hoc_phan_id": lop_moi_id
                })
                
                self.lop_hoc_phan_repo.update_so_luong(lop_moi_id, 1)
                
                # C. Log History
                # Log cancellation of old
                self.lich_su_repo.upsert_and_log(
                    sinh_vien_id, 
                    hoc_ky_id, 
                    str(dang_ky_cu.id), 
                    "huy_dang_ky"
                )
                # Log registration of new
                self.lich_su_repo.upsert_and_log(
                    sinh_vien_id, 
                    hoc_ky_id, 
                    str(dang_ky_moi.id), 
                    "dang_ky"
                )
                
            return ServiceResult.ok(None, "Chuyển lớp học phần thành công")
            
        except Exception as e:
            print(f"Error transferring course: {e}")
            return ServiceResult.fail("Lỗi hệ thống khi chuyển lớp học phần", error_code="INTERNAL_ERROR")

    def _check_conflict(self, schedules1: List[Any], schedules2: List[Any]) -> bool:
        """
        Check if any schedule in list 1 overlaps with list 2
        """
        for s1 in schedules1:
            for s2 in schedules2:
                if s1.thu != s2.thu:
                    continue
                if s1.tiet_bat_dau < s2.tiet_ket_thuc and s2.tiet_bat_dau < s1.tiet_ket_thuc:
                    return True
        return False
