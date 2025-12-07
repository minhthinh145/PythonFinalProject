"""
Application Layer - Tu Choi De Xuat Hoc Phan by Truong Khoa Use Case
"""
from typing import Optional
from core.types import ServiceResult


class TuChoiDeXuatHocPhanByTKUseCase:
    """
    Use case for Truong Khoa to reject de xuat hoc phan
    
    Business Rules:
    - TK can only reject de xuat belonging to their khoa
    - De xuat trang_thai becomes 'tu_choi'
    """
    
    def __init__(self, tk_repo, de_xuat_repo):
        self.tk_repo = tk_repo
        self.de_xuat_repo = de_xuat_repo
    
    def execute(
        self, 
        user_id: str, 
        de_xuat_id: str
    ) -> ServiceResult:
        """
        Execute the use case
        
        Args:
            user_id: ID of the truong khoa user
            de_xuat_id: ID of the de xuat to reject
            
        Returns:
            ServiceResult indicating success or failure
        """
        try:
            # Step 1: Get truong khoa
            truong_khoa = self.tk_repo.find_by_user_id(user_id)
            if not truong_khoa:
                return ServiceResult.fail(
                    "Không tìm thấy trưởng khoa",
                    error_code="TRUONG_KHOA_NOT_FOUND"
                )
            
            # Step 2: Get de xuat
            de_xuat = self.de_xuat_repo.find_by_id(de_xuat_id)
            if not de_xuat:
                return ServiceResult.fail(
                    "Không tìm thấy đề xuất học phần",
                    error_code="DE_XUAT_NOT_FOUND"
                )
            
            # Step 3: Check if de xuat belongs to TK's khoa
            if str(de_xuat['khoa_id']) != str(truong_khoa['khoa_id']):
                return ServiceResult.fail(
                    "Bạn không có quyền từ chối đề xuất này",
                    error_code="FORBIDDEN"
                )
            
            # Step 4: Reject
            success = self.de_xuat_repo.reject(
                de_xuat_id=de_xuat_id,
                nguoi_tu_choi_id=str(truong_khoa['id'])
            )
            
            if success:
                return ServiceResult.ok(
                    None,
                    "Từ chối đề xuất học phần thành công"
                )
            else:
                return ServiceResult.fail(
                    "Không thể từ chối đề xuất học phần",
                    error_code="UPDATE_FAILED"
                )
                
        except Exception as e:
            import logging
            logging.error(f"Error in TuChoiDeXuatHocPhanByTKUseCase: {e}")
            return ServiceResult.fail(
                "Lỗi hệ thống khi từ chối đề xuất học phần",
                error_code="INTERNAL_ERROR"
            )
