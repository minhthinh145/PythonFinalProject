"""
Application Layer - GV Use Case: Get Lop Hoc Phan List
"""
from core.types import ServiceResult
from application.gv.interfaces import IGVLopHocPhanRepository, GVLopHocPhanDTO
from typing import Optional, List, Dict, Any


class GetGVLopHocPhanListUseCase:
    """
    Use case to get list of LopHocPhan assigned to a GiangVien
    """
    
    def __init__(self, lhp_repository: IGVLopHocPhanRepository):
        self.lhp_repository = lhp_repository
    
    def execute(self, gv_user_id: str, hoc_ky_id: Optional[str] = None) -> ServiceResult:
        """
        Execute get list logic
        
        Args:
            gv_user_id: UUID of the GiangVien's user account
            hoc_ky_id: Optional filter by semester
            
        Returns:
            ServiceResult with list of LopHocPhan
        """
        try:
            lhp_list: List[GVLopHocPhanDTO] = self.lhp_repository.get_lop_hoc_phan_by_gv(
                gv_user_id, hoc_ky_id
            )
            
            # Map DTOs to response format (camelCase for frontend)
            response_list = [
                self._map_to_response(lhp) for lhp in lhp_list
            ]
            
            # Return array directly - FE expects result.data to be array
            return ServiceResult.ok(response_list)
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, lhp: GVLopHocPhanDTO) -> Dict[str, Any]:
        """Map DTO to snake_case response (matches FE types)"""
        return {
            "id": lhp.id,
            "ma_lop": lhp.ma_lop,
            "so_luong_hien_tai": lhp.so_luong_hien_tai,
            "so_luong_toi_da": lhp.so_luong_toi_da,
            "hoc_phan": {
                "ten_hoc_phan": lhp.hoc_phan.get("ten_hoc_phan"),
                "mon_hoc": {
                    "ma_mon": lhp.hoc_phan.get("mon_hoc", {}).get("ma_mon"),
                    "ten_mon": lhp.hoc_phan.get("mon_hoc", {}).get("ten_mon"),
                    "so_tin_chi": lhp.hoc_phan.get("mon_hoc", {}).get("so_tin_chi"),
                }
            }
        }
