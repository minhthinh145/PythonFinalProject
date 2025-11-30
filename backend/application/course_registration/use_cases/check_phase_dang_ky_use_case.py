"""
Application Layer - Check Phase Dang Ky Use Case
"""
from core.types import ServiceResult
from application.enrollment.interfaces import IKyPhaseRepository

class CheckPhaseDangKyUseCase:
    """
    Use case to check if course registration phase is active
    """
    
    def __init__(self, ky_phase_repo: IKyPhaseRepository):
        self.ky_phase_repo = ky_phase_repo
        
    def execute(self, hoc_ky_id: str) -> ServiceResult:
        """
        Execute check logic
        """
        # Get current enabled phase
        current_phase = self.ky_phase_repo.get_current_phase(hoc_ky_id)
        
        if not current_phase:
            return ServiceResult.fail("Chưa có phase nào đang mở", error_code="NO_ACTIVE_PHASE")
            
        # Check if it is course registration phase
        if current_phase.phase == "dang_ky_hoc_phan":
            return ServiceResult.ok(None, "Phase đăng ký học phần đang mở")
        else:
            return ServiceResult.fail(
                f"Đang ở phase: {current_phase.phase}. Chưa đến phase đăng ký học phần",
                error_code="WRONG_PHASE"
            )
