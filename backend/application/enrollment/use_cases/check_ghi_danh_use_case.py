"""
Application Layer - Check Ghi Danh Use Case
"""
from core.types import ServiceResult
from application.enrollment.interfaces import (
    IHocKyRepository,
    IKyPhaseRepository,
    IDotDangKyRepository
)
from application.sinh_vien.interfaces import ISinhVienRepository

class CheckGhiDanhUseCase:
    """
    Use case to check if student can enroll
    """
    
    def __init__(
        self,
        hoc_ky_repo: IHocKyRepository,
        ky_phase_repo: IKyPhaseRepository,
        dot_dang_ky_repo: IDotDangKyRepository,
        sinh_vien_repo: ISinhVienRepository
    ):
        self.hoc_ky_repo = hoc_ky_repo
        self.ky_phase_repo = ky_phase_repo
        self.dot_dang_ky_repo = dot_dang_ky_repo
        self.sinh_vien_repo = sinh_vien_repo
        
    def execute(self, user_id: str) -> ServiceResult:
        """
        Execute check logic
        """
        # 1. Check student info
        sinh_vien = self.sinh_vien_repo.get_by_id(user_id)
        if not sinh_vien or not sinh_vien.khoa_id:
            return ServiceResult.fail("Sinh viên không tồn tại hoặc chưa có khoa")
            
        # 2. Check current semester
        current_hoc_ky = self.hoc_ky_repo.get_current_hoc_ky()
        if not current_hoc_ky:
            return ServiceResult.fail("Chưa có học kỳ hiện hành")
            
        # 3. Check current phase
        current_phase = self.ky_phase_repo.get_current_phase(current_hoc_ky.id)
        if not current_phase:
            return ServiceResult.fail("Chưa có giai đoạn hiện hành")
            
        if current_phase.phase != "ghi_danh":
            return ServiceResult.fail("Chưa đến giai đoạn ghi danh")
            
        # 4. Check registration period (Toan truong)
        dot_toan_truong = self.dot_dang_ky_repo.find_toan_truong_by_hoc_ky(current_hoc_ky.id, "ghi_danh")
        if dot_toan_truong:
            return ServiceResult.ok(None, "Đợt ghi danh toàn trường đang mở, sinh viên có thể ghi danh")
            
        # 5. Check registration period (Theo khoa)
        dot_theo_khoa = self.dot_dang_ky_repo.is_ghi_danh_for_khoa(sinh_vien.khoa_id, current_hoc_ky.id)
        if dot_theo_khoa:
            return ServiceResult.ok(None, "Đợt ghi danh theo khoa đang mở, sinh viên có thể ghi danh")
            
        return ServiceResult.fail("Không có đợt ghi danh nào đang mở")
