from core.types import ServiceResult
from application.pdt.interfaces.repositories import IDeXuatHocPhanRepository

class TuChoiDeXuatHocPhanUseCase:
    def __init__(self, de_xuat_repo: IDeXuatHocPhanRepository):
        self.de_xuat_repo = de_xuat_repo

    def execute(self, proposal_id: str, reason: str) -> ServiceResult:
        try:
            if not proposal_id:
                return ServiceResult.fail("Thiếu proposal_id", error_code="MISSING_PARAMS")
            
            if not reason:
                return ServiceResult.fail("Cần cung cấp lý do từ chối", error_code="MISSING_REASON")

            success = self.de_xuat_repo.reject_proposal(proposal_id, reason)
            
            if success:
                return ServiceResult.ok(None, "Từ chối đề xuất thành công")
            else:
                return ServiceResult.fail("Không tìm thấy đề xuất hoặc lỗi hệ thống", error_code="NOT_FOUND")
        except Exception as e:
            return ServiceResult.fail(str(e))
