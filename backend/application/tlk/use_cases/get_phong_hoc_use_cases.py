"""
Application Layer - TLK Use Case: Get Phong Hoc
"""
from core.types import ServiceResult
from application.tlk.interfaces import ITLKRepository, TLKPhongHocDTO
from typing import List, Dict, Any


class GetPhongHocByTLKUseCase:
    """
    Use case to get list of Phong Hoc for TLK's khoa
    """
    
    def __init__(self, tlk_repository: ITLKRepository):
        self.tlk_repository = tlk_repository
    
    def execute(self, user_id: str) -> ServiceResult:
        """
        Execute get phong hoc logic
        
        Args:
            user_id: UUID of the TLK user
            
        Returns:
            ServiceResult with list of PhongHoc
        """
        try:
            # Get TLK's khoa
            khoa_id = self.tlk_repository.get_khoa_id_by_user(user_id)
            if not khoa_id:
                return ServiceResult.forbidden("Không xác định khoa của trợ lý khoa")
            
            # Get phong hoc by khoa
            phong_hoc_list = self.tlk_repository.get_phong_hoc_by_khoa(khoa_id)
            
            # Map to response format (camelCase for frontend)
            response_list = [
                self._map_to_response(ph) for ph in phong_hoc_list
            ]
            
            return ServiceResult.ok({"phongHoc": response_list})
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, ph: TLKPhongHocDTO) -> Dict[str, Any]:
        """Map DTO to camelCase response"""
        return {
            "id": ph.id,
            "maPhong": ph.ma_phong,
            "tenCoSo": ph.ten_co_so,
            "sucChua": ph.suc_chua,
        }


class GetAvailablePhongHocUseCase:
    """
    Use case to get list of available (unassigned) Phong Hoc
    """
    
    def __init__(self, tlk_repository: ITLKRepository):
        self.tlk_repository = tlk_repository
    
    def execute(self, user_id: str) -> ServiceResult:
        """
        Execute get available phong hoc logic
        
        Args:
            user_id: UUID of the TLK user
            
        Returns:
            ServiceResult with list of available PhongHoc
        """
        try:
            # Get TLK's khoa
            khoa_id = self.tlk_repository.get_khoa_id_by_user(user_id)
            if not khoa_id:
                return ServiceResult.forbidden("Không xác định khoa của trợ lý khoa")
            
            # Get available phong hoc
            phong_hoc_list = self.tlk_repository.get_available_phong_hoc(khoa_id)
            
            # Map to response format (camelCase for frontend)
            response_list = [
                {
                    "id": ph.id,
                    "maPhong": ph.ma_phong,
                    "tenCoSo": ph.ten_co_so,
                    "sucChua": ph.suc_chua,
                }
                for ph in phong_hoc_list
            ]
            
            return ServiceResult.ok({"phongHoc": response_list})
            
        except Exception as e:
            return ServiceResult.fail(str(e))
