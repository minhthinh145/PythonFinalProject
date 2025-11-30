
import pytest
from unittest.mock import Mock, MagicMock
from application.course_registration.use_cases.get_danh_sach_lop_da_dang_ky_use_case import GetDanhSachLopDaDangKyUseCase
from application.course_registration.interfaces import IDangKyHocPhanRepository
from infrastructure.persistence.models import DangKyHocPhan, LopHocPhan, HocPhan, MonHoc, GiangVien, Users

class TestGetDanhSachLopDaDangKyUseCase:
    @pytest.fixture
    def mock_dkhp_repo(self):
        return Mock(spec=IDangKyHocPhanRepository)

    @pytest.fixture
    def use_case(self, mock_dkhp_repo):
        return GetDanhSachLopDaDangKyUseCase(mock_dkhp_repo)

    def test_execute_success(self, use_case, mock_dkhp_repo):
        # Arrange
        sinh_vien_id = "sv-1"
        hoc_ky_id = "hk-1"
        
        # Mock registered class
        dk1 = MagicMock(spec=DangKyHocPhan)
        lhp1 = MagicMock(spec=LopHocPhan)
        lhp1.id = "lhp-1"
        lhp1.ma_lop = "L01"
        lhp1.so_luong_hien_tai = 10
        lhp1.so_luong_toi_da = 50
        lhp1.hoc_phan.mon_hoc.ma_mon = "M01"
        lhp1.hoc_phan.mon_hoc.ten_mon = "Mon 1"
        lhp1.hoc_phan.mon_hoc.so_tin_chi = 3
        lhp1.giang_vien.id.ho_ten = "GV A"
        lhp1.lichhocdinhky_set = MagicMock()
        lhp1.lichhocdinhky_set.all.return_value = []
        dk1.lop_hoc_phan = lhp1
        
        mock_dkhp_repo.find_by_sinh_vien_and_hoc_ky.return_value = [dk1]
        
        # Act
        result = use_case.execute(sinh_vien_id, hoc_ky_id)
        
        # Assert
        assert result.success is True
        data = result.data
        
        assert len(data) == 1
        assert data[0]["maMon"] == "M01"
        assert len(data[0]["danhSachLop"]) == 1
        assert data[0]["danhSachLop"][0]["id"] == "lhp-1"
