"""
Unit tests for GetHocKyHienHanhUseCase

Following TDD approach:
1. Write test first
2. Implement use case
3. Verify test passes
"""
import pytest
from unittest.mock import Mock, MagicMock
from core.types import ServiceResult
from application.common.use_cases.get_hoc_ky_hien_hanh_use_case import GetHocKyHienHanhUseCase


class TestGetHocKyHienHanhUseCase:
    """Test suite for GetHocKyHienHanhUseCase"""
    
    @pytest.fixture
    def mock_hoc_ky_repo(self):
        """Mock HocKy repository"""
        return Mock()
    
    @pytest.fixture
    def mock_nien_khoa_repo(self):
        """Mock NienKhoa repository"""
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_hoc_ky_repo, mock_nien_khoa_repo):
        """Create use case instance with mocks"""
        return GetHocKyHienHanhUseCase(mock_hoc_ky_repo, mock_nien_khoa_repo)
    
    def test_get_hoc_ky_hien_hanh_success(self, use_case, mock_hoc_ky_repo, mock_nien_khoa_repo):
        """Test successful retrieval of current semester"""
        # Arrange
        mock_hoc_ky = MagicMock()
        mock_hoc_ky.id = "hk-123"
        mock_hoc_ky.ten_hoc_ky = "Học kỳ 1"
        mock_hoc_ky.ma_hoc_ky = 1
        mock_hoc_ky.id_nien_khoa_id = "nk-456"
        from datetime import date
        mock_hoc_ky.ngay_bat_dau = date(2024, 9, 1)
        mock_hoc_ky.ngay_ket_thuc = date(2025, 1, 15)
        mock_hoc_ky.hien_hanh = True
        
        mock_nien_khoa = MagicMock()
        mock_nien_khoa.id = "nk-456"
        mock_nien_khoa.ten_nien_khoa = "2024-2025"
        
        mock_hoc_ky_repo.find_hien_hanh.return_value = mock_hoc_ky
        mock_nien_khoa_repo.find_by_id.return_value = mock_nien_khoa
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert result.data is not None
        assert result.data['id'] == "hk-123"
        assert result.data['tenHocKy'] == "Học kỳ 1"
        assert result.data['maHocKy'] == 1
        assert result.data['nienKhoa']['id'] == "nk-456"
        assert result.data['nienKhoa']['tenNienKhoa'] == "2024-2025"
        assert result.data['ngayBatDau'] == "2024-09-01"
        assert result.data['ngayKetThuc'] == "2025-01-15"
    
    def test_get_hoc_ky_hien_hanh_not_found(self, use_case, mock_hoc_ky_repo):
        """Test when no current semester exists"""
        # Arrange
        mock_hoc_ky_repo.find_hien_hanh.return_value = None
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True  # Still success but with null data
        assert result.data is None
        assert "Không có học kỳ hiện hành" in result.message
    
    def test_get_hoc_ky_hien_hanh_with_null_dates(self, use_case, mock_hoc_ky_repo, mock_nien_khoa_repo):
        """Test handling of null dates"""
        # Arrange
        mock_hoc_ky = MagicMock()
        mock_hoc_ky.id = "hk-123"
        mock_hoc_ky.ten_hoc_ky = "Học kỳ 1"
        mock_hoc_ky.ma_hoc_ky = 1
        mock_hoc_ky.id_nien_khoa_id = "nk-456"
        mock_hoc_ky.ngay_bat_dau = None
        mock_hoc_ky.ngay_ket_thuc = None
        
        mock_nien_khoa = MagicMock()
        mock_nien_khoa.id = "nk-456"
        mock_nien_khoa.ten_nien_khoa = "2024-2025"
        
        mock_hoc_ky_repo.find_hien_hanh.return_value = mock_hoc_ky
        mock_nien_khoa_repo.find_by_id.return_value = mock_nien_khoa
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert result.data['ngayBatDau'] is None
        assert result.data['ngayKetThuc'] is None
    
    def test_get_hoc_ky_hien_hanh_repository_error(self, use_case, mock_hoc_ky_repo):
        """Test handling of repository errors"""
        # Arrange
        mock_hoc_ky_repo.find_hien_hanh.side_effect = Exception("Database connection error")
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is False
        assert "error" in result.message.lower() or "lỗi" in result.message.lower()
