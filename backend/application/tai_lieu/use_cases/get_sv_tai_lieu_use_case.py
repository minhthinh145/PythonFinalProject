"""
Get TaiLieu for SinhVien Use Case
"""
from typing import List, Dict, Any
from core.types.service_result import ServiceResult
from application.tai_lieu.interfaces.repositories import ITaiLieuRepository


class GetSVTaiLieuUseCase:
    """
    Get list of TaiLieu for a LopHocPhan
    Only SV who is enrolled in the LHP can access
    """
    
    def __init__(self, repository: ITaiLieuRepository):
        self.repository = repository
    
    def execute(self, lhp_id: str, sv_user_id: str) -> ServiceResult:
        """
        Get TaiLieu for a LopHocPhan
        
        Args:
            lhp_id: UUID of LopHocPhan
            sv_user_id: UUID of SinhVien's user account
            
        Returns:
            ServiceResult with list of TaiLieu (SVTaiLieuDTO format)
        """
        # Check if student is enrolled
        is_enrolled = self.repository.is_student_enrolled(lhp_id, sv_user_id)
        
        if not is_enrolled:
            return ServiceResult.fail(
                message="Không có quyền truy cập lớp học phần này",
                error_code="FORBIDDEN"
            )
        
        # Get documents
        documents = self.repository.find_by_lop_hoc_phan(lhp_id)
        
        # Convert to response format matching frontend SVTaiLieuDTO
        result = []
        for doc in documents:
            result.append({
                "id": doc.id,
                "tenTaiLieu": doc.ten_tai_lieu,
                "fileType": doc.file_type,
                "fileUrl": "",  # Will be generated on download
                "uploadedAt": doc.created_at or "",
                "uploadedBy": doc.uploaded_by_name or "",
            })
        
        return ServiceResult.ok(
            data=result,
            message="Lấy danh sách tài liệu thành công"
        )
