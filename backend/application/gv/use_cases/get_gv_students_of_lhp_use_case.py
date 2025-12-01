"""
Application Layer - GV Use Case: Get Students of Lop Hoc Phan
"""
from core.types import ServiceResult
from application.gv.interfaces import IGVLopHocPhanRepository, GVStudentDTO
from typing import List, Dict, Any


class GetGVStudentsOfLHPUseCase:
    """
    Use case to get students registered in a LopHocPhan (only if GV is assigned)
    """
    
    def __init__(self, lhp_repository: IGVLopHocPhanRepository):
        self.lhp_repository = lhp_repository
    
    def execute(self, lhp_id: str, gv_user_id: str) -> ServiceResult:
        """
        Execute get students logic
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of the GiangVien's user account
            
        Returns:
            ServiceResult with list of students
        """
        try:
            # First verify GV owns this LHP
            if not self.lhp_repository.verify_gv_owns_lhp(lhp_id, gv_user_id):
                return ServiceResult.forbidden("Bạn không có quyền xem lớp học phần này")
            
            students = self.lhp_repository.get_students_of_lhp(lhp_id, gv_user_id)
            
            # Map DTOs to response format (camelCase for frontend)
            response_list = [
                self._map_to_response(student) for student in (students or [])
            ]
            
            return ServiceResult.ok({"sinhVien": response_list})
            
        except Exception as e:
            return ServiceResult.fail(str(e))
    
    def _map_to_response(self, student: GVStudentDTO) -> Dict[str, Any]:
        """Map DTO to camelCase response"""
        return {
            "id": student.id,
            "mssv": student.mssv,
            "hoTen": student.hoTen,
            "lop": student.lop,
            "email": student.email,
        }
