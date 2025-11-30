from core.types import ServiceResult
from application.pdt.interfaces.repositories import IDeXuatHocPhanRepository

class DuyetDeXuatHocPhanUseCase:
    def __init__(self, de_xuat_repo: IDeXuatHocPhanRepository):
        self.de_xuat_repo = de_xuat_repo

    def execute(self, proposal_id: str) -> ServiceResult:
        if not proposal_id:
            return ServiceResult.fail("Missing proposal ID", error_code="MISSING_PARAMS")

        success = self.de_xuat_repo.approve_proposal(proposal_id)
        
        if success:
            return ServiceResult.ok({"message": "Proposal approved successfully"})
        else:
            return ServiceResult.fail("Proposal not found or could not be approved", error_code="NOT_FOUND")
