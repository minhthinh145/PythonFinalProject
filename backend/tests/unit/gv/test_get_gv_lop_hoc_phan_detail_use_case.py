"""
Unit Tests for GetGVLopHocPhanDetailUseCase
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

from application.gv.interfaces import IGVLopHocPhanRepository, GVLopHocPhanDetailDTO


class TestGetGVLopHocPhanDetailUseCase:
    """Tests for GetGVLopHocPhanDetailUseCase"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock repository for testing"""
        return Mock(spec=IGVLopHocPhanRepository)
    
    @pytest.fixture
    def use_case(self, mock_repo):
        """UseCase instance with mocked dependencies"""
        from application.gv.use_cases import GetGVLopHocPhanDetailUseCase
        return GetGVLopHocPhanDetailUseCase(mock_repo)
    
    def test_execute_success_returns_detail(self, use_case, mock_repo):
        """
        Given: GV is assigned to the LopHocPhan
        When: GetGVLopHocPhanDetailUseCase.execute() is called
        Then: Return ServiceResult with LopHocPhan detail
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-001"
        mock_detail = GVLopHocPhanDetailDTO(
            id="lhp-001",
            ma_lop="LHP001",
            hoc_phan={
                "ten_hoc_phan": "Lập trình Python",
                "mon_hoc": {"ma_mon": "CS101", "ten_mon": "Lập trình", "so_tin_chi": 3}
            }
        )
        mock_repo.get_lop_hoc_phan_detail.return_value = mock_detail
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is True
        assert result.data["id"] == "lhp-001"
        assert result.data["maLop"] == "LHP001"
        assert result.data["hocPhan"]["tenHocPhan"] == "Lập trình Python"
        mock_repo.get_lop_hoc_phan_detail.assert_called_once_with(lhp_id, gv_user_id)
    
    def test_execute_not_found_when_lhp_not_exists(self, use_case, mock_repo):
        """
        Given: LopHocPhan does not exist
        When: GetGVLopHocPhanDetailUseCase.execute() is called
        Then: Return ServiceResult.not_found
        """
        # Arrange
        gv_user_id = "gv-user-123"
        lhp_id = "lhp-not-exists"
        mock_repo.get_lop_hoc_phan_detail.return_value = None
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is False
        assert result.status_code == 404
    
    def test_execute_not_found_when_gv_not_assigned(self, use_case, mock_repo):
        """
        Given: GV is NOT assigned to the LopHocPhan
        When: GetGVLopHocPhanDetailUseCase.execute() is called
        Then: Return ServiceResult.not_found (security: don't reveal existence)
        """
        # Arrange
        gv_user_id = "gv-other-user"
        lhp_id = "lhp-001"
        mock_repo.get_lop_hoc_phan_detail.return_value = None  # Repo returns None for unassigned
        
        # Act
        result = use_case.execute(lhp_id, gv_user_id)
        
        # Assert
        assert result.success is False
        assert result.status_code == 404
    
    def test_execute_failure_on_db_error(self, use_case, mock_repo):
        """
        Given: Database error occurs
        When: GetGVLopHocPhanDetailUseCase.execute() is called
        Then: Return ServiceResult with failure
        """
        # Arrange
        mock_repo.get_lop_hoc_phan_detail.side_effect = Exception("DB Error")
        
        # Act
        result = use_case.execute("lhp-001", "gv-user-123")
        
        # Assert
        assert result.success is False
