"""
Unit Tests for CheckGhiDanhUseCase
"""
import pytest
from unittest.mock import Mock

from application.enrollment.use_cases import CheckGhiDanhUseCase
from application.enrollment.interfaces import (
    IHocKyRepository,
    IKyPhaseRepository,
    IDotDangKyRepository
)
from application.sinh_vien.interfaces import ISinhVienRepository
from domain.sinh_vien.entities import SinhVienEntity

class TestCheckGhiDanhUseCase:
    
    @pytest.fixture
    def mock_hoc_ky_repo(self):
        return Mock(spec=IHocKyRepository)
        
    @pytest.fixture
    def mock_ky_phase_repo(self):
        return Mock(spec=IKyPhaseRepository)
        
    @pytest.fixture
    def mock_dot_dang_ky_repo(self):
        return Mock(spec=IDotDangKyRepository)
        
    @pytest.fixture
    def mock_sinh_vien_repo(self):
        return Mock(spec=ISinhVienRepository)
        
    @pytest.fixture
    def use_case(self, mock_hoc_ky_repo, mock_ky_phase_repo, mock_dot_dang_ky_repo, mock_sinh_vien_repo):
        return CheckGhiDanhUseCase(
            mock_hoc_ky_repo,
            mock_ky_phase_repo,
            mock_dot_dang_ky_repo,
            mock_sinh_vien_repo
        )
        
    def test_execute_success_toan_truong(self, use_case, mock_hoc_ky_repo, mock_ky_phase_repo, mock_dot_dang_ky_repo, mock_sinh_vien_repo):
        # Arrange
        user_id = "user-1"
        mock_sinh_vien_repo.get_by_id.return_value = Mock(khoa_id="KHOA1")
        
        mock_hoc_ky = Mock(id="HK1")
        mock_hoc_ky_repo.get_current_hoc_ky.return_value = mock_hoc_ky
        
        mock_phase = Mock(phase="ghi_danh")
        mock_ky_phase_repo.get_current_phase.return_value = mock_phase
        
        mock_dot_dang_ky_repo.find_toan_truong_by_hoc_ky.return_value = Mock()
        
        # Act
        result = use_case.execute(user_id)
        
        # Assert
        assert result.success is True
        assert result.message == "Đợt ghi danh toàn trường đang mở, sinh viên có thể ghi danh"
        
    def test_execute_fail_no_hoc_ky(self, use_case, mock_hoc_ky_repo, mock_sinh_vien_repo):
        user_id = "user-1"
        mock_sinh_vien_repo.get_by_id.return_value = Mock(khoa_id="KHOA1")
        mock_hoc_ky_repo.get_current_hoc_ky.return_value = None
        
        result = use_case.execute(user_id)
        
        assert result.success is False
        assert result.message == "Chưa có học kỳ hiện hành"
