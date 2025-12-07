"""
Upload TaiLieu Use Case - For GV
"""
from typing import BinaryIO, Dict, Any, Optional
from core.types.service_result import ServiceResult
from application.tai_lieu.interfaces.repositories import ITaiLieuRepository, CreateTaiLieuDTO


class UploadTaiLieuUseCase:
    """
    Upload TaiLieu to S3 and save metadata to DB
    Only GV who owns the LHP can upload
    """
    
    # Max file size: 100MB
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    def __init__(self, repository: ITaiLieuRepository, s3_service):
        self.repository = repository
        self.s3_service = s3_service
    
    def execute(
        self,
        lhp_id: str,
        gv_user_id: str,
        file_obj: BinaryIO,
        filename: str,
        content_type: str,
        file_size: int,
        ten_tai_lieu: Optional[str] = None
    ) -> ServiceResult:
        """
        Upload TaiLieu
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of GiangVien's user account
            file_obj: File-like object
            filename: Original filename
            content_type: MIME type
            file_size: Size in bytes
            ten_tai_lieu: Custom name for the document
            
        Returns:
            ServiceResult with uploaded document info
        """
        # Validate file size
        if file_size > self.MAX_FILE_SIZE:
            return ServiceResult.fail(
                message="File vượt quá giới hạn 100MB",
                error_code="FILE_TOO_LARGE"
            )
        
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
        
        # Check S3 availability
        if not self.s3_service.is_available:
            return ServiceResult.fail(
                message="Dịch vụ lưu trữ không khả dụng",
                error_code="S3_UNAVAILABLE"
            )
        
        # Upload to S3
        upload_result = self.s3_service.upload_file(
            file_obj=file_obj,
            filename=filename,
            lop_hoc_phan_id=lhp_id,
            content_type=content_type
        )
        
        if not upload_result:
            return ServiceResult.fail(
                message="Lỗi khi upload file lên S3",
                error_code="S3_UPLOAD_FAILED"
            )
        
        # Save metadata to DB
        create_dto = CreateTaiLieuDTO(
            lop_hoc_phan_id=lhp_id,
            ten_tai_lieu=ten_tai_lieu or filename,
            file_path=upload_result['key'],
            file_type=content_type,
            uploaded_by=gv_user_id
        )
        
        try:
            document = self.repository.create(create_dto)
        except Exception as e:
            # Rollback: delete from S3 if DB save fails
            self.s3_service.delete_file(upload_result['key'])
            return ServiceResult.fail(
                message=f"Lỗi khi lưu metadata: {str(e)}",
                error_code="DB_SAVE_FAILED"
            )
        
        # Return response matching frontend UploadTaiLieuResponse
        return ServiceResult.ok(
            data={
                "id": document.id,
                "tenTaiLieu": document.ten_tai_lieu,
                "fileType": document.file_type,
                "fileUrl": "",  # Don't return public URL, frontend should use presigned URL via getPreviewUrl
            },
            message="Upload tài liệu thành công"
        )
