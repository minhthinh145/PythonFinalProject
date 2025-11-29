"""
Unit Tests for ChuyenLopHocPhanUseCase
"""
import pytest
from unittest.mock import Mock, patch
from application.course_registration.use_cases import ChuyenLopHocPhanUseCase
from application.course_registration.interfaces import (
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository,
    ILopHocPhanRepository,
    ILichHocDinhKyRepository
)
from application.enrollment.interfaces import IHocPhanRepository

class TestChuyenLopHocPhanUseCase:
    
    @pytest.fixture(autouse=True)
    def mock_transaction(self):
        with patch('django.db.transaction.atomic'):
            yield

    @pytest.fixture
    def mock_repos(self):
        return {
            'dang_ky_hp': Mock(spec=IDangKyHocPhanRepository),
            'lop_hoc_phan': Mock(spec=ILopHocPhanRepository),
            'hoc_phan': Mock(spec=IHocPhanRepository),
            'dang_ky_tkb': Mock(spec=IDangKyTKBRepository),
            'lich_su': Mock(spec=ILichSuDangKyRepository),
            'lich_hoc': Mock(spec=ILichHocDinhKyRepository)
        }

    @pytest.fixture
    def use_case(self, mock_repos):
        return ChuyenLopHocPhanUseCase(
            mock_repos['dang_ky_hp'],
            mock_repos['lop_hoc_phan'],
            mock_repos['hoc_phan'],
            mock_repos['dang_ky_tkb'],
            mock_repos['lich_su'],
            mock_repos['lich_hoc']
        )

    def test_execute_success(self, use_case, mock_repos):
        # Arrange
        user_id = "user-1"
        request_data = {"lopHocPhanIdCu": "LHP1", "lopHocPhanIdMoi": "LHP2"}
        
        # 1. Old DangKy exists
        mock_dk = Mock(id="DK1", trang_thai="da_dang_ky")
        mock_dk.lop_hoc_phan.hoc_phan.mon_hoc_id = "MH1"
        mock_dk.lop_hoc_phan.hoc_phan.id_hoc_ky = "HK1"
        mock_repos['dang_ky_hp'].find_by_sinh_vien_and_lop_hoc_phan.return_value = mock_dk
        
        # 2. New LHP exists
        mock_lhp_moi = Mock(id="LHP2", hoc_phan_id="HP2", so_luong_hien_tai=10, so_luong_toi_da=50, ma_lop="L02")
        mock_repos['lop_hoc_phan'].find_by_id.return_value = mock_lhp_moi
        
        # 3. Same MonHoc
        mock_hp_moi = Mock(id="HP2", mon_hoc_id="MH1", id_hoc_ky="HK1")
        mock_hp_moi.mon_hoc.ma_mon = "M01"
        mock_repos['hoc_phan'].find_by_id.return_value = mock_hp_moi
        
        # 4. TKB Conflict check (mocking no conflict)
        mock_repos['dang_ky_tkb'].find_registered_lop_hoc_phans_by_hoc_ky.return_value = []
        mock_repos['lich_hoc'].find_by_lop_hoc_phan.return_value = [Mock(thu=2, tiet_bat_dau=1, tiet_ket_thuc=3)]
        
        # Act
        result = use_case.execute(request_data, user_id)
        
        # Assert
        assert result.success is True
        assert result.message == "Chuyển lớp học phần thành công"
        mock_repos['dang_ky_hp'].update_lop_hoc_phan.assert_called_with("DK1", "LHP2")
        mock_repos['dang_ky_tkb'].update_lop_hoc_phan.assert_called_with("DK1", "LHP2")
        mock_repos['lich_su'].upsert_and_log.assert_called_with(user_id, "HK1", "DK1", "dang_ky")
        mock_repos['lop_hoc_phan'].update_so_luong.assert_any_call("LHP1", -1)
        mock_repos['lop_hoc_phan'].update_so_luong.assert_any_call("LHP2", 1)

    def test_execute_fail_old_class_not_found(self, use_case, mock_repos):
        mock_repos['dang_ky_hp'].find_by_sinh_vien_and_lop_hoc_phan.return_value = None
        result = use_case.execute({"lopHocPhanIdCu": "LHP1", "lopHocPhanIdMoi": "LHP2"}, "user-1")
        assert result.success is False
        assert result.error_code == "OLD_CLASS_NOT_FOUND"

    def test_execute_fail_different_subject(self, use_case, mock_repos):
        mock_dk = Mock(id="DK1", trang_thai="da_dang_ky")
        mock_dk.lop_hoc_phan.hoc_phan.mon_hoc_id = "MH1"
        mock_repos['dang_ky_hp'].find_by_sinh_vien_and_lop_hoc_phan.return_value = mock_dk
        
        mock_lhp_moi = Mock(id="LHP2", hoc_phan_id="HP2")
        mock_repos['lop_hoc_phan'].find_by_id.return_value = mock_lhp_moi
        
        mock_hp_moi = Mock(id="HP2", mon_hoc_id="MH2") # Different MonHoc
        mock_repos['hoc_phan'].find_by_id.return_value = mock_hp_moi
        
        result = use_case.execute({"lopHocPhanIdCu": "LHP1", "lopHocPhanIdMoi": "LHP2"}, "user-1")
        assert result.success is False
        assert result.error_code == "DIFFERENT_SUBJECT"
