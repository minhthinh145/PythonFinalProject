"""
Unit Tests for DangKyLopHocPhanUseCase
"""
import pytest
from unittest.mock import Mock, MagicMock
from application.course_registration.use_cases import DangKyLopHocPhanUseCase
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository,
    ILichHocDinhKyRepository
)
from application.enrollment.interfaces import (
    IKyPhaseRepository,
    IGhiDanhRepository,
    IHocPhanRepository
)
from unittest.mock import patch

class TestDangKyLopHocPhanUseCase:
    
    @pytest.fixture(autouse=True)
    def mock_transaction(self):
        with patch('django.db.transaction.atomic'):
            yield
    
    @pytest.fixture
    def mock_repos(self):
        return {
            'ky_phase': Mock(spec=IKyPhaseRepository),
            'lop_hoc_phan': Mock(spec=ILopHocPhanRepository),
            'ghi_danh': Mock(spec=IGhiDanhRepository),
            'hoc_phan': Mock(spec=IHocPhanRepository),
            'dang_ky_hp': Mock(spec=IDangKyHocPhanRepository),
            'dang_ky_tkb': Mock(spec=IDangKyTKBRepository),
            'lich_su': Mock(spec=ILichSuDangKyRepository),
            'lich_hoc': Mock(spec=ILichHocDinhKyRepository)
        }

    @pytest.fixture
    def use_case(self, mock_repos):
        return DangKyLopHocPhanUseCase(
            mock_repos['ky_phase'],
            mock_repos['lop_hoc_phan'],
            mock_repos['ghi_danh'],
            mock_repos['hoc_phan'],
            mock_repos['dang_ky_hp'],
            mock_repos['dang_ky_tkb'],
            mock_repos['lich_su'],
            mock_repos['lich_hoc']
        )

    def test_execute_success(self, use_case, mock_repos):
        # Arrange
        user_id = "user-1"
        request_data = {"lopHocPhanId": "LHP1", "hocKyId": "HK1"}
        
        # 1. Phase open
        mock_repos['ky_phase'].get_current_phase.return_value = Mock(phase="dang_ky_hoc_phan")
        
        # 2. LHP exists
        mock_lhp = Mock(id="LHP1", hoc_phan_id="HP1", so_luong_hien_tai=10, so_luong_toi_da=50, ma_lop="L01")
        mock_repos['lop_hoc_phan'].find_by_id.return_value = mock_lhp
        
        # 3. Ghi danh exists
        mock_repos['ghi_danh'].is_already_registered.return_value = True
        
        # 4. Mon hoc exists & Not duplicate
        mock_hp = Mock(id="HP1", mon_hoc_id="MH1")
        mock_repos['hoc_phan'].find_by_id.return_value = mock_hp
        mock_repos['dang_ky_hp'].has_registered_mon_hoc_in_hoc_ky.return_value = False
        
        # 5. Not already registered this class
        mock_repos['dang_ky_hp'].is_student_registered.return_value = False
        
        # 6. No TKB conflict
        # Mock existing schedule
        mock_repos['dang_ky_tkb'].find_registered_lop_hoc_phans_by_hoc_ky.return_value = []
        # Mock new class schedule
        mock_repos['lich_hoc'].find_by_lop_hoc_phan.return_value = [
            Mock(thu=2, tiet_bat_dau=1, tiet_ket_thuc=3)
        ]
        
        # Mock creation return
        mock_repos['dang_ky_hp'].create.return_value = Mock(id="DK1")
        
        # Act
        result = use_case.execute(request_data, user_id)
        
        # Assert
        assert result.success is True
        assert result.message == "Đăng ký học phần thành công"
        mock_repos['dang_ky_hp'].create.assert_called_once()
        mock_repos['lich_su'].upsert_and_log.assert_called_once()
        mock_repos['dang_ky_tkb'].create.assert_called_once()
        mock_repos['lop_hoc_phan'].update_so_luong.assert_called_with("LHP1", 1)

    def test_execute_fail_phase_closed(self, use_case, mock_repos):
        mock_repos['ky_phase'].get_current_phase.return_value = None
        result = use_case.execute({"lopHocPhanId": "LHP1", "hocKyId": "HK1"}, "user-1")
        assert result.success is False
        assert result.error_code == "PHASE_NOT_OPEN"

    def test_execute_fail_lhp_full(self, use_case, mock_repos):
        mock_repos['ky_phase'].get_current_phase.return_value = Mock(phase="dang_ky_hoc_phan")
        mock_lhp = Mock(id="LHP1", hoc_phan_id="HP1", so_luong_hien_tai=50, so_luong_toi_da=50)
        mock_repos['lop_hoc_phan'].find_by_id.return_value = mock_lhp
        mock_repos['ghi_danh'].is_already_registered.return_value = True
        mock_hp = Mock(id="HP1", mon_hoc_id="MH1")
        mock_repos['hoc_phan'].find_by_id.return_value = mock_hp
        mock_repos['dang_ky_hp'].has_registered_mon_hoc_in_hoc_ky.return_value = False
        
        result = use_case.execute({"lopHocPhanId": "LHP1", "hocKyId": "HK1"}, "user-1")
        assert result.success is False
        assert result.error_code == "LHP_FULL"

    def test_execute_fail_tkb_conflict(self, use_case, mock_repos):
        # Setup basic checks pass
        mock_repos['ky_phase'].get_current_phase.return_value = Mock(phase="dang_ky_hoc_phan")
        mock_lhp = Mock(id="LHP1", hoc_phan_id="HP1", so_luong_hien_tai=10, so_luong_toi_da=50, ma_lop="L01")
        mock_repos['lop_hoc_phan'].find_by_id.return_value = mock_lhp
        mock_repos['ghi_danh'].is_already_registered.return_value = True
        mock_hp = Mock(id="HP1", mon_hoc_id="MH1")
        mock_repos['hoc_phan'].find_by_id.return_value = mock_hp
        mock_repos['dang_ky_hp'].has_registered_mon_hoc_in_hoc_ky.return_value = False
        mock_repos['dang_ky_hp'].is_student_registered.return_value = False
        
        # Setup Conflict
        # Existing class: Monday, 1-3
        mock_existing_lhp = Mock(id="LHP2", ma_lop="L02")
        mock_existing_lhp.hoc_phan.ten_hoc_phan = "Mon Cu"
        mock_repos['dang_ky_tkb'].find_registered_lop_hoc_phans_by_hoc_ky.return_value = [
            Mock(lop_hoc_phan=mock_existing_lhp)
        ]
        mock_repos['lich_hoc'].find_by_lop_hoc_phan.side_effect = lambda lhp_id: \
            [Mock(thu=2, tiet_bat_dau=1, tiet_ket_thuc=3)] if lhp_id == "LHP2" else \
            [Mock(thu=2, tiet_bat_dau=2, tiet_ket_thuc=4)] # New class: Monday, 2-4 (Overlap 2-3)
            
        result = use_case.execute({"lopHocPhanId": "LHP1", "hocKyId": "HK1"}, "user-1")
        
        assert result.success is False
        assert result.error_code == "TKB_CONFLICT"
