
import pytest
from unittest.mock import Mock, MagicMock
from datetime import date
from application.course_registration.use_cases.get_danh_sach_lop_hoc_phan_use_case import GetDanhSachLopHocPhanUseCase
from application.course_registration.interfaces import ILopHocPhanRepository, IDangKyHocPhanRepository
from infrastructure.persistence.models import LopHocPhan, HocPhan, MonHoc, GiangVien, Users, LichHocDinhKy, Phong

class TestGetDanhSachLopHocPhanUseCase:
    @pytest.fixture
    def mock_lhp_repo(self):
        return Mock(spec=ILopHocPhanRepository)

    @pytest.fixture
    def mock_dkhp_repo(self):
        return Mock(spec=IDangKyHocPhanRepository)

    @pytest.fixture
    def use_case(self, mock_lhp_repo, mock_dkhp_repo):
        return GetDanhSachLopHocPhanUseCase(mock_lhp_repo, mock_dkhp_repo)

    def test_execute_success(self, use_case, mock_lhp_repo, mock_dkhp_repo):
        # Arrange
        sinh_vien_id = "sv-1"
        hoc_ky_id = "hk-1"
        
        # Mock registered classes
        mock_dkhp_repo.find_registered_class_ids.return_value = ["lhp-registered"]
        
        # Mock classes
        # Class 1: Mon Chung (should be in monChung)
        lhp1 = MagicMock(spec=LopHocPhan)
        lhp1.id = "lhp-1"
        lhp1.ma_lop = "L01"
        lhp1.so_luong_hien_tai = 10
        lhp1.so_luong_toi_da = 50
        lhp1.hoc_phan.mon_hoc.ma_mon = "M01"
        lhp1.hoc_phan.mon_hoc.ten_mon = "Mon Chung"
        lhp1.hoc_phan.mon_hoc.so_tin_chi = 2
        lhp1.hoc_phan.mon_hoc.la_mon_chung = True
        lhp1.hoc_phan.mon_hoc.loai_mon = "dai_cuong"
        lhp1.giang_vien.id.ho_ten = "GV A"
        lhp1.lichhocdinhky_set = MagicMock()
        lhp1.lichhocdinhky_set.all.return_value = []
        
        # Class 2: Chuyen Nganh (should be in batBuoc)
        lhp2 = MagicMock(spec=LopHocPhan)
        lhp2.id = "lhp-2"
        lhp2.ma_lop = "L02"
        lhp2.hoc_phan.mon_hoc.ma_mon = "M02"
        lhp2.hoc_phan.mon_hoc.ten_mon = "Chuyen Nganh"
        lhp2.hoc_phan.mon_hoc.la_mon_chung = False
        lhp2.hoc_phan.mon_hoc.loai_mon = "chuyen_nganh"
        lhp2.lichhocdinhky_set = MagicMock()
        lhp2.lichhocdinhky_set.all.return_value = []
        
        # Class 3: Tu Chon (should be in tuChon)
        lhp3 = MagicMock(spec=LopHocPhan)
        lhp3.id = "lhp-3"
        lhp3.ma_lop = "L03"
        lhp3.hoc_phan.mon_hoc.ma_mon = "M03"
        lhp3.hoc_phan.mon_hoc.ten_mon = "Tu Chon"
        lhp3.hoc_phan.mon_hoc.la_mon_chung = False
        lhp3.hoc_phan.mon_hoc.loai_mon = "tu_chon"
        lhp3.lichhocdinhky_set = MagicMock()
        lhp3.lichhocdinhky_set.all.return_value = []
        
        # Class 4: Registered (should be skipped)
        lhp4 = MagicMock(spec=LopHocPhan)
        lhp4.id = "lhp-registered"
        
        mock_lhp_repo.find_all_by_hoc_ky.return_value = [lhp1, lhp2, lhp3, lhp4]
        
        # Act
        result = use_case.execute(sinh_vien_id, hoc_ky_id)
        
        # Assert
        assert result.success is True
        data = result.data
        
        # Check monChung
        assert len(data["monChung"]) == 1
        assert data["monChung"][0]["maMon"] == "M01"
        assert len(data["monChung"][0]["danhSachLop"]) == 1
        assert data["monChung"][0]["danhSachLop"][0]["id"] == "lhp-1"
        
        # Check batBuoc
        assert len(data["batBuoc"]) == 1
        assert data["batBuoc"][0]["maMon"] == "M02"
        
        # Check tuChon
        assert len(data["tuChon"]) == 1
        assert data["tuChon"][0]["maMon"] == "M03"
        
        # Check registered filtered out
        all_ids = []
        for group in [data["monChung"], data["batBuoc"], data["tuChon"]]:
            for mon in group:
                for lop in mon["danhSachLop"]:
                    all_ids.append(lop["id"])
                    
        assert "lhp-registered" not in all_ids
