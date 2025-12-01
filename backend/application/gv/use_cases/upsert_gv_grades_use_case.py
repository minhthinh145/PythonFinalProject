"""
Application Layer - GV Use Case: Upsert Grades of Lop Hoc Phan
"""
from core.types import ServiceResult
from application.gv.interfaces import IGVLopHocPhanRepository, IGVGradeRepository
from typing import List, Dict, Any


class UpsertGVGradesUseCase:
    """
    Use case to insert or update grades of students in a LopHocPhan (only if GV is assigned)
    """
    
    def __init__(
        self, 
        lhp_repository: IGVLopHocPhanRepository,
        grade_repository: IGVGradeRepository
    ):
        self.lhp_repository = lhp_repository
        self.grade_repository = grade_repository
    
    def execute(
        self, 
        lhp_id: str, 
        gv_user_id: str, 
        grades: List[Dict[str, Any]]
    ) -> ServiceResult:
        """
        Execute upsert grades logic
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of the GiangVien's user account
            grades: List of {sinhVienId, diemSo}
            
        Returns:
            ServiceResult with success/failure
        """
        try:
            # First verify GV owns this LHP
            if not self.lhp_repository.verify_gv_owns_lhp(lhp_id, gv_user_id):
                return ServiceResult.forbidden("Bạn không có quyền cập nhật điểm lớp học phần này")
            
            # Validate input
            if not grades:
                return ServiceResult.fail("Danh sách điểm không được rỗng")
            
            # Validate grades format
            for grade in grades:
                if "sinhVienId" not in grade:
                    return ServiceResult.fail("Thiếu thông tin sinh viên")
                if "diemSo" not in grade:
                    return ServiceResult.fail("Thiếu thông tin điểm")
                diem = grade.get("diemSo")
                if diem is not None and (diem < 0 or diem > 10):
                    return ServiceResult.fail("Điểm phải từ 0 đến 10")
            
            # Validate all students are registered in LHP
            sinh_vien_ids = [g["sinhVienId"] for g in grades]
            if not self.grade_repository.validate_students_in_lhp(lhp_id, sinh_vien_ids):
                return ServiceResult.fail("Một số sinh viên không thuộc lớp học phần này")
            
            # Map from camelCase to snake_case for repository
            mapped_grades = [
                {"sinh_vien_id": g["sinhVienId"], "diem_so": g["diemSo"]}
                for g in grades
            ]
            
            # Execute upsert
            success = self.grade_repository.upsert_grades(lhp_id, mapped_grades)
            
            if success:
                return ServiceResult.ok({"message": "Cập nhật điểm thành công"})
            else:
                return ServiceResult.fail("Không thể cập nhật điểm")
            
        except Exception as e:
            return ServiceResult.fail(str(e))
