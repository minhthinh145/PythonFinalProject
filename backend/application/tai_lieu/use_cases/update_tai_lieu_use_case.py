"""
Update TaiLieu Use Case - For GV
"""
from core.types.service_result import ServiceResult
from application.tai_lieu.interfaces.repositories import ITaiLieuRepository


class UpdateTaiLieuUseCase:
    """
    Update TaiLieu name (file stays the same on S3)
    Only GV who owns the LHP can update
    """
    
    def __init__(self, repository: ITaiLieuRepository):
        self.repository = repository
    
    def execute(self, lhp_id: str, doc_id: str, gv_user_id: str, new_name: str) -> ServiceResult:
        """
        Update TaiLieu name
        
        Args:
            lhp_id: UUID of LopHocPhan
            doc_id: UUID of TaiLieu
            gv_user_id: UUID of GiangVien's user account
            new_name: New name for the document
            
        Returns:
            ServiceResult with updated document info
        """
        # Validate name
        if not new_name or not new_name.strip():
            return ServiceResult.fail(
                message="Tên tài liệu không được để trống",
                error_code="INVALID_NAME"
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
        
        # Get document to verify it exists and belongs to LHP
        document = self.repository.find_by_id(doc_id)
        
        if not document:
            return ServiceResult.fail(
                message="Tài liệu không tồn tại",
                error_code="DOCUMENT_NOT_FOUND"
            )
        
        # Update name
        updated = self.repository.update_name(doc_id, new_name.strip())
        
        if not updated:
            return ServiceResult.fail(
                message="Lỗi khi cập nhật tài liệu",
                error_code="UPDATE_FAILED"
            )
        
        return ServiceResult.ok(
            data={
                "id": updated.id,
                "ten_tai_lieu": updated.ten_tai_lieu,
                "file_path": updated.file_path,
            },
            message="Cập nhật tên tài liệu thành công"
        )
