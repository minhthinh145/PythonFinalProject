"""
Application Layer - TLK Get Giang Vien Use Case
"""
from dataclasses import dataclass
from typing import List, Optional

from core.types.service_result import ServiceResult
from application.tlk.interfaces import ITLKRepository, TLKGiangVienDTO


@dataclass
class GetGiangVienByKhoaUseCase:
    """
    Use case for getting all Giang Vien belonging to TLK's khoa
    """
    repository: ITLKRepository
    
    def execute(self, user_id: str, mon_hoc_id: Optional[str] = None) -> ServiceResult:
        """
        Get all Giang Vien for the TLK's khoa
        
        Args:
            user_id: The TLK user ID
            mon_hoc_id: Optional - filter by mon_hoc (future enhancement)
            
        Returns:
            ServiceResult with list of GiangVien DTOs
        """
        try:
            # Get khoa_id from TLK user
            khoa_id = self.repository.get_khoa_id_by_user(user_id)
            
            if not khoa_id:
                return ServiceResult.failure_result(
                    message="Không tìm thấy thông tin khoa của trợ lý khoa",
                    error_code="TLK_KHOA_NOT_FOUND"
                )
            
            # Get giang vien list
            giang_viens = self.repository.get_giang_vien_by_khoa(khoa_id)
            
            # Convert DTOs to dict
            data = [
                {
                    "id": gv.id,
                    "ho_ten": gv.ho_ten,
                }
                for gv in giang_viens
            ]
            
            return ServiceResult.success_result(
                data=data,
                message=f"Đã tải {len(data)} giảng viên"
            )
            
        except Exception as e:
            return ServiceResult.failure_result(
                message=f"Lỗi khi tải danh sách giảng viên: {str(e)}",
                error_code="TLK_GIANGVIEN_ERROR"
            )
