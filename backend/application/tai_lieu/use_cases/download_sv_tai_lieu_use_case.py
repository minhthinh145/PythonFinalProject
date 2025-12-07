"""
Download TaiLieu for SinhVien Use Case
"""
from typing import Dict, Any, Optional
from core.types.service_result import ServiceResult
from application.tai_lieu.interfaces.repositories import ITaiLieuRepository


class DownloadSVTaiLieuUseCase:
    """
    Download TaiLieu from S3
    Only SV who is enrolled in the LHP can download
    """
    
    def __init__(self, repository: ITaiLieuRepository, s3_service):
        self.repository = repository
        self.s3_service = s3_service
    
    def execute(self, lhp_id: str, doc_id: str, sv_user_id: str) -> ServiceResult:
        """
        Get file info for download (returns file content)
        
        Args:
            lhp_id: UUID of LopHocPhan
            doc_id: UUID of TaiLieu
            sv_user_id: UUID of SinhVien's user account
            
        Returns:
            ServiceResult with file bytes and metadata
        """
        # Check if student is enrolled
        print(f"[DEBUG] Checking enrollment: lhp_id={lhp_id}, sv_user_id={sv_user_id}")
        is_enrolled = self.repository.is_student_enrolled(lhp_id, sv_user_id)
        print(f"[DEBUG] is_enrolled={is_enrolled}")
        
        if not is_enrolled:
            return ServiceResult.fail(
                message="Không có quyền truy cập lớp học phần này",
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
