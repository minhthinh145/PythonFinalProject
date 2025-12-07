"""
Unit Tests for GetGVStudentsOfLHPUseCase
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

from application.gv.interfaces import IGVLopHocPhanRepository, GVStudentDTO


class TestGetGVStudentsOfLHPUseCase:
    """Tests for GetGVStudentsOfLHPUseCase"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock repository for testing"""
        return Mock(spec=IGVLopHocPhanRepository)
    
    @pytest.fixture
    def use_case(self, mock_repo):
        """UseCase instance with mocked dependencies"""
        from application.gv.use_cases import GetGVStudentsOfLHPUseCase
        return GetGVStudentsOfLHPUseCase(mock_repo)
    
    def test_execute_success_returns_students(self, use_case, mock_repo):
        """
        Given: GV is assigned to LHP with registered students
        When: GetGVStudentsOfLHPUseCase.execute() is called
        Then: Return ServiceResult with list of students
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        mock_students = [
            GVStudentDTO(
                id="sv-001",
                mssv="2021001",
                ho_ten="Nguyen Van A",
                lop="K21-CNTT",
                email="nva@student.edu"
            ),
            GVStudentDTO(
                id="sv-002",
                mssv="2021002",
                ho_ten="Tran Thi B",
                lop="K21-CNTT",
                email="ttb@student.edu"
            )
        ]
        mock_repo.verify_gv_owns_lhp.return_value = True
        mock_repo.get_students_of_lhp.return_value = mock_students
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is True
        assert isinstance(result.data, list)
        assert len(result.data) == 2
        assert result.data[0]["mssv"] == "2021001"
        assert result.data[0]["ho_ten"] == "Nguyen Van A"
    
    def test_execute_empty_list_when_no_students(self, use_case, mock_repo):
        """
        Given: GV is assigned to LHP with no registered students
        When: GetGVStudentsOfLHPUseCase.execute() is called
        Then: Return ServiceResult with empty list
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-new"
        mock_repo.verify_gv_owns_lhp.return_value = True
        mock_repo.get_students_of_lhp.return_value = []
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is True
        assert result.data == []
    
    def test_execute_forbidden_when_gv_not_assigned(self, use_case, mock_repo):
        """
        Given: GV is NOT assigned to the LopHocPhan
        When: GetGVStudentsOfLHPUseCase.execute() is called
        Then: Return ServiceResult.forbidden
        """
        # Arrange
        gv_user_id = "gv-other-user"
        lhp_id = "lhp-001"
        mock_repo.verify_gv_owns_lhp.return_value = False
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is False
        assert result.status_code == 403
    
    def test_execute_failure_on_db_error(self, use_case, mock_repo):
        """
        Given: Database error occurs
        When: GetGVStudentsOfLHPUseCase.execute() is called
        Then: Return ServiceResult with failure
        """
        # Arrange
        mock_repo.verify_gv_owns_lhp.side_effect = Exception("DB Error")
        
        # Act
        result = use_case.execute("lhp-001", "gv-user-123")
        
        # Assert
        assert result.success is False
