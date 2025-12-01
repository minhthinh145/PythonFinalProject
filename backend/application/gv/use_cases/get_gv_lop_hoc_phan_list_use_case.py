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
            
            return ServiceResult.ok({"lopHocPhan": response_list})
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, lhp: GVLopHocPhanDTO) -> Dict[str, Any]:
        """Map DTO to camelCase response"""
        return {
            "id": lhp.id,
            "maLop": lhp.ma_lop,
            "soLuongHienTai": lhp.so_luong_hien_tai,
            "soLuongToiDa": lhp.so_luong_toi_da,
            "hocPhan": {
                "tenHocPhan": lhp.hoc_phan.get("ten_hoc_phan"),
                "monHoc": {
                    "maMon": lhp.hoc_phan.get("mon_hoc", {}).get("ma_mon"),
                    "tenMon": lhp.hoc_phan.get("mon_hoc", {}).get("ten_mon"),
                    "soTinChi": lhp.hoc_phan.get("mon_hoc", {}).get("so_tin_chi"),
                }
            }
        }
