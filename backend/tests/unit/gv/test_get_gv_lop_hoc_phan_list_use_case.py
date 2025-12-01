"""
Unit Tests for GetGVLopHocPhanListUseCase
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

from application.gv.interfaces import IGVLopHocPhanRepository, GVLopHocPhanDTO


class TestGetGVLopHocPhanListUseCase:
    """Tests for GetGVLopHocPhanListUseCase"""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock repository for testing"""
        return Mock(spec=IGVLopHocPhanRepository)
    
    @pytest.fixture
    def use_case(self, mock_repo):
        """UseCase instance with mocked dependencies"""
        # Import inside fixture to allow tests to run even before implementation
        from application.gv.use_cases import GetGVLopHocPhanListUseCase
        return GetGVLopHocPhanListUseCase(mock_repo)
    
    def test_execute_success_returns_list_of_lhp(self, use_case, mock_repo):
        """
        Given: GV has assigned LopHocPhan
        When: GetGVLopHocPhanListUseCase.execute() is called
        Then: Return ServiceResult with list of LopHocPhan DTOs
        """
        # Arrange
        gv_user_id = "gv-user-123"
        hoc_ky_id = "hk-123"
        mock_lhp_list = [
            GVLopHocPhanDTO(
                id="lhp-001",
                ma_lop="LHP001",
                so_luong_hien_tai=30,
                so_luong_toi_da=50,
                hoc_phan={
                    "ten_hoc_phan": "Lập trình Python",
                    "mon_hoc": {"ma_mon": "CS101", "ten_mon": "Lập trình", "so_tin_chi": 3}
                }
            ),
            GVLopHocPhanDTO(
                id="lhp-002",
                ma_lop="LHP002",
                so_luong_hien_tai=25,
                so_luong_toi_da=40,
                hoc_phan={
                    "ten_hoc_phan": "Cấu trúc dữ liệu",
                    "mon_hoc": {"ma_mon": "CS102", "ten_mon": "CTDL", "so_tin_chi": 4}
                }
            )
        ]
        mock_repo.get_lop_hoc_phan_by_gv.return_value = mock_lhp_list
        
        # Act
        result = use_case.execute(gv_user_id, hoc_ky_id)
        
        # Assert
        assert result.success is True
        assert "lopHocPhan" in result.data
        assert len(result.data["lopHocPhan"]) == 2
        assert result.data["lopHocPhan"][0]["maLop"] == "LHP001"
        assert result.data["lopHocPhan"][0]["hocPhan"]["tenHocPhan"] == "Lập trình Python"
        mock_repo.get_lop_hoc_phan_by_gv.assert_called_once_with(gv_user_id, hoc_ky_id)
    
    def test_execute_empty_list_when_no_lhp(self, use_case, mock_repo):
        """
        Given: GV has no assigned LopHocPhan
        When: GetGVLopHocPhanListUseCase.execute() is called
        Then: Return ServiceResult with empty list (not error)
        """
        # Arrange
        gv_user_id = "gv-new-user"
        hoc_ky_id = "hk-123"
        mock_repo.get_lop_hoc_phan_by_gv.return_value = []
        
        # Act
        result = use_case.execute(gv_user_id, hoc_ky_id)
        
        # Assert
        assert result.success is True
        assert result.data["lopHocPhan"] == []
    
    def test_execute_without_hoc_ky_id(self, use_case, mock_repo):
        """
        Given: GV requests list without specifying hoc_ky_id
        When: GetGVLopHocPhanListUseCase.execute() is called with hoc_ky_id=None
        Then: Return all LHP across all semesters
        """
        # Arrange
        gv_user_id = "gv-user-123"
        mock_repo.get_lop_hoc_phan_by_gv.return_value = []
        
        # Act
        result = use_case.execute(gv_user_id, hoc_ky_id=None)
        
        # Assert
        mock_repo.get_lop_hoc_phan_by_gv.assert_called_once_with(gv_user_id, None)
        assert result.success is True
    
    def test_execute_failure_on_db_error(self, use_case, mock_repo):
        """
        Given: Database error occurs
        When: GetGVLopHocPhanListUseCase.execute() is called
        Then: Return ServiceResult with failure
        """
        # Arrange
        gv_user_id = "gv-user-123"
        mock_repo.get_lop_hoc_phan_by_gv.side_effect = Exception("Database connection error")
        
        # Act
        result = use_case.execute(gv_user_id, hoc_ky_id=None)
        
        # Assert
        assert result.success is False
        assert "Database connection error" in result.message
