"""
Application Layer - Get De Xuat Hoc Phan for Truong Khoa Use Case
"""
from typing import List, Dict, Any, Optional
from core.types import ServiceResult


class GetDeXuatHocPhanForTKUseCase:
    """
    Use case to get list of de xuat hoc phan for Truong Khoa
    
    Business Rules:
    - Only return de xuat belonging to TK's khoa
    - Only return de xuat with trang_thai = 'cho_duyet'
    """
    
    def __init__(self, tk_repo, de_xuat_repo):
        self.tk_repo = tk_repo
        self.de_xuat_repo = de_xuat_repo
    
    def execute(self, user_id: str, hoc_ky_id: Optional[str] = None) -> ServiceResult:
        """
        Execute the use case
        
        Args:
            user_id: ID of the truong khoa user
            hoc_ky_id: Optional hoc ky filter
            
        Returns:
            ServiceResult with list of DeXuatHocPhanForTruongKhoaDTO
        """
        try:
            # Step 1: Get truong khoa and their khoa_id
            truong_khoa = self.tk_repo.find_by_user_id(user_id)
            if not truong_khoa:
                return ServiceResult.fail(
                    "Không tìm thấy trưởng khoa",
                    error_code="TRUONG_KHOA_NOT_FOUND"
                )
            
            # truong_khoa is a dict from repository
            khoa_id = truong_khoa['khoa_id']
            
            # Step 2: Get de xuat list for this khoa with status 'cho_duyet'
            # Repository returns list of DeXuatHocPhanForTKDTO
            de_xuat_list = self.de_xuat_repo.find_by_khoa_and_status(
                khoa_id=khoa_id,
                trang_thai="cho_duyet"
            )
            
            # Step 3: Transform DTO to dict format that FE expects
            result = []
            for dx in de_xuat_list:
                result.append({
                    "id": dx.id,
                    "maHocPhan": dx.ma_hoc_phan,
                    "tenHocPhan": dx.ten_hoc_phan,
                    "soTinChi": dx.so_tin_chi,
                    "giangVien": dx.giang_vien,
                    "trangThai": dx.trang_thai,
                })
            
            return ServiceResult.ok(
                result,
                "Lấy danh sách đề xuất học phần thành công"
            )
            
        except Exception as e:
            import logging
            logging.error(f"Error in GetDeXuatHocPhanForTKUseCase: {e}")
            return ServiceResult.fail(
                "Lỗi hệ thống khi lấy danh sách đề xuất",
                error_code="INTERNAL_ERROR"
            )
    

