"""
Application Layer - GV Use Case: Get Grades of Lop Hoc Phan
"""
from core.types import ServiceResult
from application.gv.interfaces import IGVLopHocPhanRepository, IGVGradeRepository, GVGradeDTO
from typing import List, Dict, Any


class GetGVGradesUseCase:
    """
    Use case to get grades of students in a LopHocPhan (only if GV is assigned)
    """
    
    def __init__(
        self, 
        lhp_repository: IGVLopHocPhanRepository,
        grade_repository: IGVGradeRepository
    ):
        self.lhp_repository = lhp_repository
        self.grade_repository = grade_repository
    
    def execute(self, lhp_id: str, gv_user_id: str) -> ServiceResult:
        """
        Execute get grades logic
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of the GiangVien's user account
            
        Returns:
            ServiceResult with list of grades
        """
        try:
            # First verify GV owns this LHP
            if not self.lhp_repository.verify_gv_owns_lhp(lhp_id, gv_user_id):
                return ServiceResult.forbidden("Bạn không có quyền xem điểm lớp học phần này")
            
            grades = self.grade_repository.get_grades(lhp_id)
            
            # Map DTOs to response format (camelCase for frontend)
            response_list = [
                self._map_to_response(grade) for grade in grades
            ]
            
            # Return array directly - FE expects result.data to be array
            return ServiceResult.ok(response_list)
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, grade: GVGradeDTO) -> Dict[str, Any]:
        """Map DTO to snake_case response (matches FE types)"""
        return {
            "sinh_vien_id": grade.sinh_vien_id,
            "diem_so": grade.diem_so,
        }
