from typing import List, Dict, Any
from core.types import ServiceResult
from application.pdt.interfaces.repositories import IDeXuatHocPhanRepository

class GetDeXuatHocPhanUseCase:
    def __init__(self, de_xuat_repo: IDeXuatHocPhanRepository):
        self.de_xuat_repo = de_xuat_repo

    def execute(self) -> ServiceResult:
        proposals = self.de_xuat_repo.get_pending_proposals()
        
        # Transform to DTO if necessary, or return as is if repo returns dicts
        # Assuming repo returns model instances or dicts that need serialization
        # For now, we assume repo returns list of dicts or objects that can be serialized
        
        return ServiceResult.ok(proposals)
