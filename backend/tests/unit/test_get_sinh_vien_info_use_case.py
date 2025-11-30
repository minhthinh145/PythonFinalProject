"""
Unit Tests for GetSinhVienInfoUseCase
"""
import pytest
from unittest.mock import Mock
from datetime import date

from application.sinh_vien.use_cases import GetSinhVienInfoUseCase
from application.sinh_vien.interfaces import ISinhVienRepository
from domain.sinh_vien.entities import SinhVienEntity

class TestGetSinhVienInfoUseCase:
    
    @pytest.fixture
    def mock_repo(self):
        return Mock(spec=ISinhVienRepository)
        
    @pytest.fixture
    def use_case(self, mock_repo):
        return GetSinhVienInfoUseCase(mock_repo)
        
    def test_execute_success(self, use_case, mock_repo):
        # Arrange
        user_id = "user-123"
        mock_entity = SinhVienEntity(
            id=user_id,
            ma_so_sinh_vien="SV001",
            ho_ten="Nguyen Van A",
            khoa_id="KHOA01",
            nganh_id="NGANH01",
            lop="LOP01",
            khoa_hoc="K46",
            ngay_nhap_hoc=date(2020, 9, 5),
            ten_khoa="Khoa CNTT",
            ten_nganh="Cong nghe thong tin",
            email="a@example.com"
        )
        mock_repo.get_by_id.return_value = mock_entity
        
        # Act
        result = use_case.execute(user_id)
        
        # Assert
        assert result.success is True
        assert result.data['id'] == user_id
        assert result.data['maSoSinhVien'] == "SV001"
        assert result.data['tenKhoa'] == "Khoa CNTT"
        mock_repo.get_by_id.assert_called_once_with(user_id)
        
    def test_execute_not_found(self, use_case, mock_repo):
        # Arrange
        user_id = "user-unknown"
        mock_repo.get_by_id.return_value = None
        
        # Act
        result = use_case.execute(user_id)
        
        # Assert
        assert result.success is False
        assert result.message == "Không tìm thấy thông tin sinh viên"
