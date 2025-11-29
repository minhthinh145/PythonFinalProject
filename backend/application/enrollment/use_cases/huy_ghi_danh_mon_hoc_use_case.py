from typing import List
from core.types import ServiceResult
from application.enrollment.interfaces import IGhiDanhRepository

class HuyGhiDanhMonHocUseCase:
    """
    Use case to cancel subject registration
    """
    
    def __init__(self, ghi_danh_repo: IGhiDanhRepository):
        self.ghi_danh_repo = ghi_danh_repo
        
    def execute(self, request_data: dict, user_id: str) -> ServiceResult:
        """
        Execute cancellation
        """
        ghi_danh_ids = request_data.get('ghiDanhIds')
        
        if not ghi_danh_ids or not isinstance(ghi_danh_ids, list):
            return ServiceResult.fail("Danh sách ghi danh không hợp lệ", error_code="INVALID_INPUT")
        
        self.ghi_danh_repo.delete_many(ghi_danh_ids)
        
        return ServiceResult.ok(None, "Hủy ghi danh thành công")
