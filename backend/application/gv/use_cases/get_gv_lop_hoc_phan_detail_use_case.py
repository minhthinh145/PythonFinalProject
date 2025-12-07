"""
Application Layer - GV Use Case: Get Lop Hoc Phan Detail
"""
from core.types import ServiceResult
from application.gv.interfaces import IGVLopHocPhanRepository, GVLopHocPhanDetailDTO
from typing import Dict, Any


class GetGVLopHocPhanDetailUseCase:
    """
    Use case to get detail of a LopHocPhan (only if GV is assigned)
    """
    
    def __init__(self, lhp_repository: IGVLopHocPhanRepository):
        self.lhp_repository = lhp_repository
    
    def execute(self, lhp_id: str, gv_user_id: str) -> ServiceResult:
        """
        Execute get detail logic
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of the GiangVien's user account
            
        Returns:
            ServiceResult with LopHocPhan detail
        """
        try:
            detail = self.lhp_repository.get_lop_hoc_phan_detail(lhp_id, gv_user_id)
            
            if not detail:
                return ServiceResult.not_found("Không tìm thấy lớp học phần")
            
            # Map DTO to response format (camelCase for frontend)
            response = self._map_to_response(detail)
            
            return ServiceResult.ok(response)
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, detail: GVLopHocPhanDetailDTO) -> Dict[str, Any]:
        """Map DTO to snake_case response (matches FE types)"""
        return {
            "id": detail.id,
            "ma_lop": detail.ma_lop,
            "hoc_phan": {
                "ten_hoc_phan": detail.hoc_phan.get("ten_hoc_phan"),
                "mon_hoc": {
                    "ma_mon": detail.hoc_phan.get("mon_hoc", {}).get("ma_mon"),
                    "ten_mon": detail.hoc_phan.get("mon_hoc", {}).get("ten_mon"),
                    "so_tin_chi": detail.hoc_phan.get("mon_hoc", {}).get("so_tin_chi"),
                }
            }
        }
