"""
Application Layer - Huy Dang Ky Hoc Phan Use Case
"""
from typing import Optional
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
        
    def execute(self, sinh_vien_id: str, lop_hoc_phan_id: str, hoc_ky_id: Optional[str] = None) -> ServiceResult:
        """
        Execute cancellation logic
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

            # 3. Find Registration
            dang_ky = self.dang_ky_hp_repo.find_by_sinh_vien_and_lop_hoc_phan(sinh_vien_id, lop_hoc_phan_id)
            if not dang_ky:
                return ServiceResult.fail("Chưa đăng ký lớp học phần này", error_code="REGISTRATION_NOT_FOUND")
                
            # Only da_dang_ky can be cancelled
            if dang_ky.trang_thai != "da_dang_ky":
                return ServiceResult.fail(f"Không thể hủy đăng ký với trạng thái: {dang_ky.trang_thai}", error_code="INVALID_STATUS")

            # 4. Perform Cancellation (Atomic)
            with transaction.atomic(using='neon'):
                # 4.1: Log History FIRST (before deleting dang_ky)
                self.lich_su_repo.upsert_and_log(
                    sinh_vien_id, 
                    hoc_ky_id, 
                    str(dang_ky.id), 
                    "huy_dang_ky"
                )
                
                # 4.2: Delete TKB
                self.dang_ky_tkb_repo.delete_by_dang_ky_id(str(dang_ky.id))
                
                # 4.3: DELETE DangKyHocPhan (not update status)
                # History is already tracked in lich_su_dang_ky
                self.dang_ky_hp_repo.delete(str(dang_ky.id))
                
                # 4.4: Update Quantity
                self.lop_hoc_phan_repo.update_so_luong(lop_hoc_phan_id, -1)
                
            return ServiceResult.ok(None, "Hủy đăng ký học phần thành công")
            
        except Exception as e:
            print(f"Error cancelling course: {e}")
            return ServiceResult.fail("Lỗi hệ thống khi hủy đăng ký học phần", error_code="INTERNAL_ERROR")
