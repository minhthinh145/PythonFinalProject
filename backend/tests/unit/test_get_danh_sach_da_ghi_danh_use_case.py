"""
Unit Tests for GetDanhSachDaGhiDanhUseCase
"""
import pytest
from unittest.mock import Mock

from application.enrollment.use_cases import GetDanhSachDaGhiDanhUseCase
from application.enrollment.interfaces import IGhiDanhRepository

class TestGetDanhSachDaGhiDanhUseCase:
    
    @pytest.fixture
    def mock_ghi_danh_repo(self):
        return Mock(spec=IGhiDanhRepository)
        
    @pytest.fixture
    def use_case(self, mock_ghi_danh_repo):
        return GetDanhSachDaGhiDanhUseCase(mock_ghi_danh_repo)
        
    def test_execute_success(self, use_case, mock_ghi_danh_repo):
        # Arrange
        user_id = "user-1"
        
        # Mock GhiDanh record
        mock_gd = Mock()
        mock_gd.id = "GD1"
        mock_gd.hoc_phan.id = "HP1"
        mock_gd.hoc_phan.mon_hoc.ma_mon = "M001"
        mock_gd.hoc_phan.mon_hoc.ten_mon = "Mon 1"
        mock_gd.hoc_phan.mon_hoc.so_tin_chi = 3
        mock_gd.hoc_phan.mon_hoc.khoa.ten_khoa = "Khoa CNTT"
        
        mock_de_xuat = Mock()
        mock_de_xuat.giang_vien_de_xuat.id.ho_ten = "GV A"
        mock_gd.hoc_phan.mon_hoc.dexuathocphan_set.all.return_value = [mock_de_xuat]
        
        mock_ghi_danh_repo.find_by_sinh_vien.return_value = [mock_gd]
        
        # Act
        result = use_case.execute(user_id)
        
        # Assert
        assert result.success is True
        assert len(result.data) == 1
        item = result.data[0]
        assert item['ghiDanhId'] == "GD1"
        assert item['maMonHoc'] == "M001"
        assert item['tenGiangVien'] == "GV A"
