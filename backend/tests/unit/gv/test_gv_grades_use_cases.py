"""
Unit Tests for GetGVGradesUseCase and UpsertGVGradesUseCase
TDD: RED phase - tests before implementation
"""
import pytest
from unittest.mock import Mock
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    django.setup()

from application.gv.interfaces import IGVLopHocPhanRepository, IGVGradeRepository, GVGradeDTO


class TestGetGVGradesUseCase:
    """Tests for GetGVGradesUseCase"""
    
    @pytest.fixture
    def mock_lhp_repo(self):
        """Mock LHP repository for testing"""
        return Mock(spec=IGVLopHocPhanRepository)
    
    @pytest.fixture
    def mock_grade_repo(self):
        """Mock grade repository for testing"""
        return Mock(spec=IGVGradeRepository)
    
    @pytest.fixture
    def use_case(self, mock_lhp_repo, mock_grade_repo):
        """UseCase instance with mocked dependencies"""
        from application.gv.use_cases import GetGVGradesUseCase
        return GetGVGradesUseCase(mock_lhp_repo, mock_grade_repo)
    
    def test_execute_success_returns_grades(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: GV is assigned to LHP with grades
        When: GetGVGradesUseCase.execute() is called
        Then: Return ServiceResult with list of grades
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        mock_grades = [
            GVGradeDTO(sinh_vien_id="sv-001", diem_so=8.5),
            GVGradeDTO(sinh_vien_id="sv-002", diem_so=9.0),
            GVGradeDTO(sinh_vien_id="sv-003", diem_so=None),  # Not graded yet
        ]
        mock_lhp_repo.verify_gv_owns_lhp.return_value = True
        mock_grade_repo.get_grades.return_value = mock_grades
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is True
        assert "diem" in result.data
        assert len(result.data["diem"]) == 3
        assert result.data["diem"][0]["sinhVienId"] == "sv-001"
        assert result.data["diem"][0]["diemSo"] == 8.5
        assert result.data["diem"][2]["diemSo"] is None  # Not graded
        mock_lhp_repo.verify_gv_owns_lhp.assert_called_once_with(lhp_id, gv_user_id)
    
    def test_execute_forbidden_when_gv_not_assigned(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: GV is NOT assigned to the LopHocPhan
        When: GetGVGradesUseCase.execute() is called
        Then: Return ServiceResult.forbidden
        """
        # Arrange
        mock_lhp_repo.verify_gv_owns_lhp.return_value = False
        
        # Act
        result = use_case.execute("lhp-001", "gv-other")
        
        # Assert
        assert result.success is False
        assert result.status_code == 403
    
    def test_execute_failure_on_db_error(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: Database error occurs
        When: GetGVGradesUseCase.execute() is called
        Then: Return ServiceResult with failure
        """
        # Arrange
        mock_lhp_repo.verify_gv_owns_lhp.side_effect = Exception("DB Error")
        
        # Act
        result = use_case.execute("lhp-001", "gv-user-123")
        
        # Assert
        assert result.success is False


class TestUpsertGVGradesUseCase:
    """Tests for UpsertGVGradesUseCase"""
    
    @pytest.fixture
    def mock_lhp_repo(self):
        """Mock LHP repository for testing"""
        return Mock(spec=IGVLopHocPhanRepository)
    
    @pytest.fixture
    def mock_grade_repo(self):
        """Mock grade repository for testing"""
        return Mock(spec=IGVGradeRepository)
    
    @pytest.fixture
    def use_case(self, mock_lhp_repo, mock_grade_repo):
        """UseCase instance with mocked dependencies"""
        from application.gv.use_cases import UpsertGVGradesUseCase
        return UpsertGVGradesUseCase(mock_lhp_repo, mock_grade_repo)
    
    def test_execute_success_upserts_grades(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: GV is assigned to LHP and provides valid grades
        When: UpsertGVGradesUseCase.execute() is called
        Then: Grades are upserted and return success
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        grades_input = [
            {"sinhVienId": "sv-001", "diemSo": 8.5},
            {"sinhVienId": "sv-002", "diemSo": 9.0},
        ]
        mock_lhp_repo.verify_gv_owns_lhp.return_value = True
        mock_grade_repo.validate_students_in_lhp.return_value = True
        mock_grade_repo.upsert_grades.return_value = True
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id, grades_input)
        
        # Assert
        assert result.success is True
        mock_grade_repo.upsert_grades.assert_called_once()
    
    def test_execute_forbidden_when_gv_not_assigned(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: GV is NOT assigned to the LopHocPhan
        When: UpsertGVGradesUseCase.execute() is called
        Then: Return ServiceResult.forbidden
        """
        # Arrange
        mock_lhp_repo.verify_gv_owns_lhp.return_value = False
        
        # Act
        result = use_case.execute("lhp-001", "gv-other", [])
        
        # Assert
        assert result.success is False
        assert result.status_code == 403
    
    def test_execute_fail_when_student_not_in_lhp(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: One of the students is not registered in the LHP
        When: UpsertGVGradesUseCase.execute() is called
        Then: Return ServiceResult.fail with validation error
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        grades_input = [
            {"sinhVienId": "sv-not-in-lhp", "diemSo": 8.5},
        ]
        mock_lhp_repo.verify_gv_owns_lhp.return_value = True
        mock_grade_repo.validate_students_in_lhp.return_value = False
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id, grades_input)
        
        # Assert
        assert result.success is False
        assert result.status_code == 400
    
    def test_execute_fail_when_invalid_grade_value(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: Grade value is out of valid range (0-10)
        When: UpsertGVGradesUseCase.execute() is called
        Then: Return ServiceResult.fail with validation error
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        grades_input = [
            {"sinhVienId": "sv-001", "diemSo": 15.0},  # Invalid: > 10
        ]
        mock_lhp_repo.verify_gv_owns_lhp.return_value = True
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id, grades_input)
        
        # Assert
        assert result.success is False
        assert result.status_code == 400
    
    def test_execute_fail_when_negative_grade(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: Grade value is negative
        When: UpsertGVGradesUseCase.execute() is called
        Then: Return ServiceResult.fail with validation error
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        grades_input = [
            {"sinhVienId": "sv-001", "diemSo": -1.0},  # Invalid: < 0
        ]
        mock_lhp_repo.verify_gv_owns_lhp.return_value = True
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id, grades_input)
        
        # Assert
        assert result.success is False
        assert result.status_code == 400
    
    def test_execute_allows_null_grade(self, use_case, mock_lhp_repo, mock_grade_repo):
        """
        Given: Grade value is None (to clear a grade)
        When: UpsertGVGradesUseCase.execute() is called
        Then: Accept and process the request
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        grades_input = [
            {"sinhVienId": "sv-001", "diemSo": None},  # Clear grade
        ]
        mock_lhp_repo.verify_gv_owns_lhp.return_value = True
        mock_grade_repo.validate_students_in_lhp.return_value = True
        mock_grade_repo.upsert_grades.return_value = True
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id, grades_input)
        
        # Assert
        assert result.success is True
