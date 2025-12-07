"""
Application Layer - TLK Get TKB Batch Use Case
"""
from typing import List
from core.types.service_result import ServiceResult


class GetTKBBatchUseCase:
    """
    Use case for TLK to get TKB for multiple học phần
    Used when viewing existing schedules before creating new ones
    """
    
    def __init__(self, tkb_repo):
        self.tkb_repo = tkb_repo
    
    def execute(self, ma_hoc_phans: List[str], hoc_ky_id: str) -> ServiceResult:
        """
        Execute the use case
        
        Args:
            ma_hoc_phans: List of mã học phần
            hoc_ky_id: Học kỳ ID
        
        Returns:
            ServiceResult with list of ThoiKhoaBieuMonHocDTO
        """
        if not ma_hoc_phans:
            return ServiceResult.fail("Danh sách mã học phần không được rỗng")
        
        if not hoc_ky_id:
            return ServiceResult.fail("Học kỳ ID không được rỗng")
        
        # Get TKB data from repository
        tkb_data = self.tkb_repo.get_tkb_by_hoc_phans(ma_hoc_phans, hoc_ky_id)
        
        return ServiceResult.ok(
            message=f"Đã tải TKB cho {len(tkb_data)} học phần",
            data=tkb_data
        )
