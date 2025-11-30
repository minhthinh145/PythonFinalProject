"""
Unit Tests for GetMonHocGhiDanhUseCase
"""
import pytest
from unittest.mock import Mock

from application.enrollment.use_cases import GetMonHocGhiDanhUseCase
from application.enrollment.interfaces import (
    IHocKyRepository,
    IHocPhanRepository
)

class TestGetMonHocGhiDanhUseCase:
    
    @pytest.fixture
    def mock_hoc_ky_repo(self):
        return Mock(spec=IHocKyRepository)
        
    @pytest.fixture
    def mock_hoc_phan_repo(self):
        return Mock(spec=IHocPhanRepository)
        
    @pytest.fixture
    def use_case(self, mock_hoc_ky_repo, mock_hoc_phan_repo):
        return GetMonHocGhiDanhUseCase(
            mock_hoc_ky_repo,
            mock_hoc_phan_repo
        )
        
    def test_execute_success(self, use_case, mock_hoc_ky_repo, mock_hoc_phan_repo):
        # Arrange
        mock_hoc_ky = Mock(id="HK1")
        mock_hoc_ky_repo.get_current_hoc_ky.return_value = mock_hoc_ky
        
        # Mock HocPhan data structure (simulating Django model or dict)
        mock_hp = Mock()
        mock_hp.id = "HP1"
        mock_hp.mon_hoc.ma_mon = "M001"
        mock_hp.mon_hoc.ten_mon = "Mon 1"
        mock_hp.mon_hoc.so_tin_chi = 3
        mock_hp.mon_hoc.khoa.ten_khoa = "Khoa CNTT"
        
        # Mock de_xuat_hoc_phan relationship
        mock_de_xuat = Mock()
        mock_de_xuat.giang_vien_de_xuat.id.ho_ten = "GV A"
        mock_hp.mon_hoc.dexuathocphan_set.all.return_value = [mock_de_xuat]
        
        mock_hoc_phan_repo.find_all_open.return_value = [mock_hp]
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert len(result.data) == 1
        item = result.data[0]
        assert item['id'] == "HP1"
        assert item['maMonHoc'] == "M001"
        assert item['tenGiangVien'] == "GV A"
        
    def test_execute_no_hoc_ky(self, use_case, mock_hoc_ky_repo):
        mock_hoc_ky_repo.get_current_hoc_ky.return_value = None
        
        result = use_case.execute()
        
        assert result.success is False
        assert result.error_code == "HOC_KY_HIEN_HANH_NOT_FOUND"
