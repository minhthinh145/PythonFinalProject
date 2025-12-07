"""
Delete TaiLieu Use Case - For GV
"""
from core.types.service_result import ServiceResult
from application.tai_lieu.interfaces.repositories import ITaiLieuRepository


class DeleteTaiLieuUseCase:
    """
    Delete TaiLieu from S3 and DB
    Only GV who owns the LHP can delete
    """
    
    def __init__(self, repository: ITaiLieuRepository, s3_service):
        self.repository = repository
        self.s3_service = s3_service
    
    def execute(self, lhp_id: str, doc_id: str, gv_user_id: str) -> ServiceResult:
        """
        Delete TaiLieu
        
        Args:
            lhp_id: UUID of LopHocPhan
            doc_id: UUID of TaiLieu
            gv_user_id: UUID of GiangVien's user account
            
        Returns:
            ServiceResult with success/failure
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
        
        # Delete from S3
        if self.s3_service.is_available:
            self.s3_service.delete_file(document.file_path)
        
        # Delete from DB
        deleted = self.repository.delete(doc_id)
        
        if not deleted:
            return ServiceResult.fail(
                message="Lỗi khi xóa tài liệu",
                error_code="DELETE_FAILED"
            )
        
        return ServiceResult.ok(
            data=None,
            message="Xóa tài liệu thành công"
        )
