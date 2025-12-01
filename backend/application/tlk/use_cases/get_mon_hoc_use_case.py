"""
Application Layer - TLK Get Mon Hoc Use Case
"""
from dataclasses import dataclass
from typing import List, Optional

from core.types.service_result import ServiceResult
from application.tlk.interfaces import ITLKRepository, TLKMonHocDTO


@dataclass
class GetMonHocByKhoaUseCase:
    """
    Use case for getting all Mon Hoc belonging to TLK's khoa
    """
    repository: ITLKRepository
    
    def execute(self, user_id: str) -> ServiceResult:
        """
        Get all Mon Hoc for the TLK's khoa
        
        Args:
            user_id: The TLK user ID
            
        Returns:
            ServiceResult with list of MonHoc DTOs
        """
        try:
            # Get khoa_id from TLK user
            khoa_id = self.repository.get_khoa_id_by_user(user_id)
            
            if not khoa_id:
                return ServiceResult.failure_result(
                    message="Không tìm thấy thông tin khoa của trợ lý khoa",
                    error_code="TLK_KHOA_NOT_FOUND"
                )
            
            # Get mon hoc list
            mon_hocs = self.repository.get_mon_hoc_by_khoa(khoa_id)
            
            # Convert DTOs to dict
            data = [
                {
                    "id": mh.id,
                    "ma_mon": mh.ma_mon,
                    "ten_mon": mh.ten_mon,
                    "so_tin_chi": mh.so_tin_chi,
                }
                for mh in mon_hocs
            ]
            
            return ServiceResult.success_result(
                data=data,
                message=f"Đã tải {len(data)} môn học"
            )
            
        except Exception as e:
            return ServiceResult.failure_result(
                message=f"Lỗi khi tải danh sách môn học: {str(e)}",
                error_code="TLK_MONHOC_ERROR"
            )
