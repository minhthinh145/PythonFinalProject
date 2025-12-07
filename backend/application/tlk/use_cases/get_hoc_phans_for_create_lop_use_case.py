"""
Application Layer - TLK Use Case: Get Hoc Phans For Create Lop
"""
from core.types import ServiceResult
from application.tlk.interfaces import ITLKRepository, ITLKHocPhanRepository, TLKHocPhanForCreateLopDTO
from typing import List, Dict, Any


class GetHocPhansForCreateLopUseCase:
    """
    Use case to get list of Hoc Phans available for creating Lop Hoc Phan
    Only returns Hoc Phans that have been approved in De Xuat process
    """
    
    def __init__(
        self, 
        tlk_repository: ITLKRepository,
        hoc_phan_repository: ITLKHocPhanRepository
    ):
        self.tlk_repository = tlk_repository
        self.hoc_phan_repository = hoc_phan_repository
    
    def execute(self, user_id: str, hoc_ky_id: str) -> ServiceResult:
        """
        Execute get hoc phans logic
        
        Args:
            user_id: UUID of the TLK user
            hoc_ky_id: UUID of HocKy
            
        Returns:
            ServiceResult with list of HocPhan
        """
        try:
            # Get TLK's khoa
            khoa_id = self.tlk_repository.get_khoa_id_by_user(user_id)
            if not khoa_id:
                return ServiceResult.forbidden("Không xác định khoa của trợ lý khoa")
            
            # Get hoc phans for create lop
            hoc_phans = self.hoc_phan_repository.get_hoc_phans_for_create_lop(
                hoc_ky_id, khoa_id
            )
            
            # Map to response format (camelCase for frontend)
            response_list = [
                self._map_to_response(hp) for hp in hoc_phans
            ]
            
            # Return array directly - FE expects result.data to be array
            return ServiceResult.ok(response_list)
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, hp: TLKHocPhanForCreateLopDTO) -> Dict[str, Any]:
        """Map DTO to camelCase response"""
        return {
            "id": hp.id,  # de_xuat_id - unique key for FE
            "hocPhanId": hp.hoc_phan_id,  # actual hoc_phan.id for creating lop
            "maHocPhan": hp.ma_hoc_phan,
            "tenHocPhan": hp.ten_hoc_phan,
            "soTinChi": hp.so_tin_chi,
            "soSinhVienGhiDanh": hp.so_sinh_vien_ghi_danh,
            "tenGiangVien": hp.ten_giang_vien,
            "giangVienId": hp.giang_vien_id,
        }
