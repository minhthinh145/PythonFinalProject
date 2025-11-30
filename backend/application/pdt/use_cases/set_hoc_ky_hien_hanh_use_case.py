from core.types import ServiceResult
from application.pdt.interfaces.repositories import IHocKyRepository

class SetHocKyHienHanhUseCase:
    def __init__(self, hoc_ky_repo: IHocKyRepository):
        self.hoc_ky_repo = hoc_ky_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult:
        if not hoc_ky_id:
            return ServiceResult.fail(
                "Thiếu thông tin (hocKyId)",
                error_code="MISSING_PARAMS"
            )

        # Check if semester exists
        hoc_ky = self.hoc_ky_repo.find_by_id(hoc_ky_id)
        if not hoc_ky:
            return ServiceResult.fail(
                "Học kỳ không tồn tại",
                error_code="NOT_FOUND"
            )

        # Set current semester
        self.hoc_ky_repo.set_current_semester(hoc_ky_id)

        return ServiceResult.ok(None)
