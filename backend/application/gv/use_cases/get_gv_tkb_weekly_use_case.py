"""
Application Layer - GV Use Case: Get TKB Weekly
"""
from core.types import ServiceResult
from application.gv.interfaces import IGVTKBRepository, GVTKBItemDTO
from datetime import date
from typing import List, Dict, Any


class GetGVTKBWeeklyUseCase:
    """
    Use case to get weekly timetable for a GiangVien
    """
    
    def __init__(self, tkb_repository: IGVTKBRepository):
        self.tkb_repository = tkb_repository
    
    def execute(
        self, 
        gv_user_id: str, 
        hoc_ky_id: str,
        date_start: date,
        date_end: date
    ) -> ServiceResult:
        """
        Execute get TKB weekly logic
        
        Args:
            gv_user_id: UUID of the GiangVien's user account
            hoc_ky_id: UUID of HocKy
            date_start: Start date of week
            date_end: End date of week
            
        Returns:
            ServiceResult with list of TKB items
        """
        try:
            tkb_items = self.tkb_repository.get_tkb_weekly(
                gv_user_id, hoc_ky_id, date_start, date_end
            )
            
            # Map DTOs to response format (camelCase for frontend)
            response_list = [
                self._map_to_response(item) for item in tkb_items
            ]
            
            return ServiceResult.ok({"tkbWeekly": response_list})
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, item: GVTKBItemDTO) -> Dict[str, Any]:
        """Map DTO to camelCase response"""
        return {
            "lopHocPhanId": item.lop_hoc_phan_id,
            "maLop": item.ma_lop,
            "tenMon": item.ten_mon,
            "maMon": item.ma_mon,
            "phong": item.phong,
            "thu": item.thu,
            "tietBatDau": item.tiet_bat_dau,
            "tietKetThuc": item.tiet_ket_thuc,
            "ngayHoc": item.ngay_hoc,
        }
