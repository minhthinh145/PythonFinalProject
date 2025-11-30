"""
Application Layer - Huy Dang Ky Hoc Phan Use Case
"""
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

class HuyDangKyHocPhanUseCase:
    """
    Use case to cancel course registration
    """
    
    def __init__(
        self,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        dang_ky_hp_repo: IDangKyHocPhanRepository,
        dang_ky_tkb_repo: IDangKyTKBRepository,
        lich_su_repo: ILichSuDangKyRepository,
        ky_phase_repo: KyPhaseRepository,
        sinh_vien_repo: SinhVienRepository
    ):
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.dang_ky_hp_repo = dang_ky_hp_repo
        self.dang_ky_tkb_repo = dang_ky_tkb_repo
        self.lich_su_repo = lich_su_repo
        self.ky_phase_repo = ky_phase_repo
        self.sinh_vien_repo = sinh_vien_repo
        
    def execute(self, sinh_vien_id: str, lop_hoc_phan_id: str, hoc_ky_id: str) -> ServiceResult:
        """
        Execute cancellation logic
        """
        try:
            # 1. Validate Student
            sinh_vien = self.sinh_vien_repo.get_by_id(sinh_vien_id)
            if not sinh_vien:
                return ServiceResult.fail("Sinh viên không tồn tại", error_code="STUDENT_NOT_FOUND")

            # 2. Check Phase
            current_phase = self.ky_phase_repo.get_current_phase(hoc_ky_id)
            if not current_phase or current_phase.phase != "dang_ky_hoc_phan":
                return ServiceResult.fail(
                    "Không trong thời gian đăng ký học phần", 
                    error_code="INVALID_PHASE"
                )

            # 3. Find Registration
            dang_ky = self.dang_ky_hp_repo.find_by_sinh_vien_and_lop_hoc_phan(sinh_vien_id, lop_hoc_phan_id)
            if not dang_ky:
                return ServiceResult.fail("Chưa đăng ký lớp học phần này", error_code="REGISTRATION_NOT_FOUND")
                
            if dang_ky.trang_thai != "da_dang_ky":
                return ServiceResult.fail("Trạng thái đăng ký không hợp lệ", error_code="INVALID_STATUS")

            # 4. Perform Cancellation (Atomic)
            with transaction.atomic(using='neon'):
                # Delete TKB
                self.dang_ky_tkb_repo.delete_by_dang_ky_id(str(dang_ky.id))
                
                # Update Status
                self.dang_ky_hp_repo.update_status(str(dang_ky.id), "da_huy")
                
                # Update Quantity
                self.lop_hoc_phan_repo.update_so_luong(lop_hoc_phan_id, -1)
                
                # Log History
                self.lich_su_repo.upsert_and_log(
                    sinh_vien_id, 
                    hoc_ky_id, 
                    str(dang_ky.id), 
                    "huy_dang_ky"
                )
                
            return ServiceResult.ok(None, "Hủy đăng ký học phần thành công")
            
        except Exception as e:
            print(f"Error cancelling course: {e}")
            return ServiceResult.fail("Lỗi hệ thống khi hủy đăng ký học phần", error_code="INTERNAL_ERROR")
