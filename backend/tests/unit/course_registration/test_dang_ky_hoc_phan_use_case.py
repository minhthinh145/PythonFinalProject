
import pytest
from unittest.mock import Mock, MagicMock
from application.course_registration.use_cases.dang_ky_hoc_phan_use_case import DangKyHocPhanUseCase
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository
)
from infrastructure.persistence.enrollment.repositories import KyPhaseRepository
from infrastructure.persistence.sinh_vien.sinh_vien_repository import SinhVienRepository
from infrastructure.persistence.models import LopHocPhan, DangKyHocPhan, DangKyTkb, LichHocDinhKy

from unittest.mock import patch

# @pytest.mark.django_db(databases=['neon'])
class TestDangKyHocPhanUseCase:
    @pytest.fixture(autouse=True)
    def mock_transaction(self):
        with patch('django.db.transaction.atomic'):
            yield

    @pytest.fixture
    def mock_lhp_repo(self):
        return Mock(spec=ILopHocPhanRepository)

    @pytest.fixture
    def mock_dkhp_repo(self):
        return Mock(spec=IDangKyHocPhanRepository)

    @pytest.fixture
    def mock_tkb_repo(self):
        return Mock(spec=IDangKyTKBRepository)

    @pytest.fixture
    def mock_lich_su_repo(self):
        return Mock(spec=ILichSuDangKyRepository)

    @pytest.fixture
    def mock_ky_phase_repo(self):
        return Mock(spec=KyPhaseRepository)

    @pytest.fixture
    def mock_sinh_vien_repo(self):
        return Mock(spec=SinhVienRepository)

    @pytest.fixture
    def use_case(self, mock_lhp_repo, mock_dkhp_repo, mock_tkb_repo, mock_lich_su_repo, mock_ky_phase_repo, mock_sinh_vien_repo):
        return DangKyHocPhanUseCase(
            mock_lhp_repo,
            mock_dkhp_repo,
            mock_tkb_repo,
            mock_lich_su_repo,
            mock_ky_phase_repo,
            mock_sinh_vien_repo
        )

    def test_execute_success(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_lhp_repo, mock_dkhp_repo, mock_tkb_repo):
        # Arrange
        sinh_vien_id = "sv-1"
        lop_hoc_phan_id = "lhp-1"
        hoc_ky_id = "hk-1"
        
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        
        phase = MagicMock()
        phase.phase = "dang_ky_hoc_phan"
        mock_ky_phase_repo.get_current_phase.return_value = phase
        
        lhp = MagicMock(spec=LopHocPhan)
        lhp.so_luong_hien_tai = 10
        lhp.so_luong_toi_da = 50
        lhp.hoc_phan.mon_hoc_id = "mon-1"
        lhp.lichhocdinhky_set.all.return_value = []
        mock_lhp_repo.find_by_id.return_value = lhp
        
        mock_dkhp_repo.has_registered_mon_hoc_in_hoc_ky.return_value = False
        mock_tkb_repo.find_registered_lop_hoc_phans_by_hoc_ky.return_value = []
        
        mock_dkhp_repo.create.return_value = MagicMock(id="dk-1")
        
        # Act
        result = use_case.execute(sinh_vien_id, lop_hoc_phan_id, hoc_ky_id)
        
        # Assert
        assert result.success is True
        mock_dkhp_repo.create.assert_called_once()
        mock_tkb_repo.create.assert_called_once()
        mock_lhp_repo.update_so_luong.assert_called_with(lop_hoc_phan_id, 1)

    def test_execute_fail_invalid_phase(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo):
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="wrong_phase")
        
        result = use_case.execute("sv-1", "lhp-1", "hk-1")
        
        assert result.success is False
        assert result.error_code == "INVALID_PHASE"

    def test_execute_fail_class_full(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_lhp_repo):
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="dang_ky_hoc_phan")
        
        lhp = MagicMock(spec=LopHocPhan)
        lhp.so_luong_hien_tai = 50
        lhp.so_luong_toi_da = 50
        mock_lhp_repo.find_by_id.return_value = lhp
        
        result = use_case.execute("sv-1", "lhp-1", "hk-1")
        
        assert result.success is False
        assert result.error_code == "CLASS_FULL"

    def test_execute_fail_time_conflict(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_lhp_repo, mock_dkhp_repo, mock_tkb_repo):
        # Arrange
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="dang_ky_hoc_phan")
        
        # New class: Mon 2, Tiet 1-3
        new_lhp = MagicMock(spec=LopHocPhan)
        new_lhp.so_luong_hien_tai = 0
        new_lhp.so_luong_toi_da = 50
        new_lhp.hoc_phan.mon_hoc_id = "mon-new"
        
        new_schedule = MagicMock(spec=LichHocDinhKy)
        new_schedule.thu = 2
        new_schedule.tiet_bat_dau = 1
        new_schedule.tiet_ket_thuc = 3
        new_lhp.lichhocdinhky_set.all.return_value = [new_schedule]
        
        mock_lhp_repo.find_by_id.return_value = new_lhp
        mock_dkhp_repo.has_registered_mon_hoc_in_hoc_ky.return_value = False
        
        # Existing registration: Mon 2, Tiet 2-4 (Overlap at 2,3)
        existing_reg = MagicMock(spec=DangKyTkb)
        existing_lhp = MagicMock(spec=LopHocPhan)
        existing_lhp.ma_lop = "LHP-EXIST"
        
        existing_schedule = MagicMock(spec=LichHocDinhKy)
        existing_schedule.thu = 2
        existing_schedule.tiet_bat_dau = 2
        existing_schedule.tiet_ket_thuc = 4
        
        existing_lhp.lichhocdinhky_set.all.return_value = [existing_schedule]
        existing_reg.lop_hoc_phan = existing_lhp
        
        mock_tkb_repo.find_registered_lop_hoc_phans_by_hoc_ky.return_value = [existing_reg]
        
        # Act
        result = use_case.execute("sv-1", "lhp-new", "hk-1")
        
        # Assert
        assert result.success is False
        assert result.error_code == "TIME_CONFLICT"
