"""
Unit Tests for GhiDanhMonHocUseCase
"""
import pytest
from unittest.mock import Mock

from application.enrollment.use_cases import GhiDanhMonHocUseCase
from application.enrollment.interfaces import (
    IHocPhanRepository,
    IGhiDanhRepository
)

class TestGhiDanhMonHocUseCase:
    
    @pytest.fixture
    def mock_hoc_phan_repo(self):
        return Mock(spec=IHocPhanRepository)
        
    @pytest.fixture
    def mock_ghi_danh_repo(self):
        return Mock(spec=IGhiDanhRepository)
        
    @pytest.fixture
    def use_case(self, mock_hoc_phan_repo, mock_ghi_danh_repo):
        return GhiDanhMonHocUseCase(
            mock_hoc_phan_repo,
            mock_ghi_danh_repo
        )
        
    def test_execute_success(self, use_case, mock_hoc_phan_repo, mock_ghi_danh_repo):
        # Arrange
        user_id = "user-1"
        mon_hoc_id = "HP1"
        request_data = {"monHocId": mon_hoc_id}
        
        mock_hp = Mock(trang_thai_mo=True)
        mock_hoc_phan_repo.find_by_id.return_value = mock_hp
        
        mock_ghi_danh_repo.is_already_registered.return_value = False
        
        # Act
        result = use_case.execute(request_data, user_id)
        
        # Assert
        assert result.success is True
        assert result.message == "Ghi danh môn học thành công"
        mock_ghi_danh_repo.create.assert_called_once()
        
    def test_execute_fail_hoc_phan_not_found(self, use_case, mock_hoc_phan_repo):
        mock_hoc_phan_repo.find_by_id.return_value = None
        
        result = use_case.execute({"monHocId": "HP1"}, "user-1")
        
        assert result.success is False
        assert result.error_code == "HOC_PHAN_NOT_FOUND"
        
    def test_execute_fail_already_registered(self, use_case, mock_hoc_phan_repo, mock_ghi_danh_repo):
        mock_hp = Mock(trang_thai_mo=True)
        mock_hoc_phan_repo.find_by_id.return_value = mock_hp
        mock_ghi_danh_repo.is_already_registered.return_value = True
        
        result = use_case.execute({"monHocId": "HP1"}, "user-1")
        
        assert result.success is False
        assert result.error_code == "ALREADY_REGISTERED"
