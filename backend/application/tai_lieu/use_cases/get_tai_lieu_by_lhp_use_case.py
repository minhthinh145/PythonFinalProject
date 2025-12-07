"""
Get TaiLieu by LopHocPhan Use Case - For GV
"""
from typing import List, Dict, Any
from core.types.service_result import ServiceResult
from application.tai_lieu.interfaces.repositories import ITaiLieuRepository


class GetTaiLieuByLHPUseCase:
    """
    Get list of TaiLieu for a LopHocPhan
    Only GV who owns the LHP can access
    """
    
    def __init__(self, repository: ITaiLieuRepository):
        self.repository = repository
    
    def execute(self, lhp_id: str, gv_user_id: str) -> ServiceResult:
        """
        Get TaiLieu for a LopHocPhan
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of GiangVien's user account
            
        Returns:
            ServiceResult with list of TaiLieu
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
        
        # Get documents
        documents = self.repository.find_by_lop_hoc_phan(lhp_id)
        
        # Convert to response format matching frontend GVDocumentDTO
        result = []
        for doc in documents:
            result.append({
                "id": doc.id,
                "ten_tai_lieu": doc.ten_tai_lieu,
                "file_path": doc.file_path,
                "file_type": doc.file_type,
                "created_at": doc.created_at,
            })
        
        return ServiceResult.ok(
            data=result,
            message="Lấy danh sách tài liệu thành công"
        )
