"""
Download TaiLieu Use Case - For GV
"""
from typing import Dict, Any, Optional
from core.types.service_result import ServiceResult
from application.tai_lieu.interfaces.repositories import ITaiLieuRepository


class DownloadTaiLieuUseCase:
    """
    Get presigned URL or stream file from S3
    Only GV who owns the LHP can download
    """
    
    def __init__(self, repository: ITaiLieuRepository, s3_service):
        self.repository = repository
        self.s3_service = s3_service
    
    def execute(self, lhp_id: str, doc_id: str, gv_user_id: str) -> ServiceResult:
        """
        Get file info for download (returns file content)
        
        Args:
            lhp_id: UUID of LopHocPhan
            doc_id: UUID of TaiLieu
            gv_user_id: UUID of GiangVien's user account
            
        Returns:
            ServiceResult with file bytes and metadata
        """
        # Check if GV owns this LHP
        owner_id = self.repository.get_lop_hoc_phan_owner(lhp_id)
        
        if not owner_id:
            return ServiceResult.fail(
                message="Lớp học phần không tồn tại",
                error_code="LHP_NOT_FOUND"
            )
        
        if owner_id != gv_user_id:
            return ServiceResult.fail(
                message="Không có quyền truy cập",
                error_code="FORBIDDEN"
            )
        
        # Get document
        document = self.repository.find_by_id(doc_id)
        
        if not document:
            return ServiceResult.fail(
                message="Tài liệu không tồn tại",
                error_code="DOCUMENT_NOT_FOUND"
            )
        
        # Check S3 availability
        if not self.s3_service.is_available:
            return ServiceResult.fail(
                message="Dịch vụ lưu trữ không khả dụng",
                error_code="S3_UNAVAILABLE"
            )
        
        # Download file from S3
        file_bytes = self.s3_service.download_file(document.file_path)
        
        if not file_bytes:
            return ServiceResult.fail(
                message="Không thể tải file từ S3",
                error_code="S3_DOWNLOAD_FAILED"
            )
        
        # Extract filename from file_path
        filename = document.file_path.split('/')[-1] if '/' in document.file_path else document.file_path
        
        return ServiceResult.ok(
            data={
                "content": file_bytes,
                "content_type": document.file_type or "application/octet-stream",
                "filename": filename,
                "ten_tai_lieu": document.ten_tai_lieu,
            },
            message="Tải file thành công"
        )
