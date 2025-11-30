
import pytest
from unittest.mock import Mock, MagicMock
from application.course_registration.use_cases.huy_dang_ky_hoc_phan_use_case import HuyDangKyHocPhanUseCase
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository
)
from infrastructure.persistence.enrollment.repositories import KyPhaseRepository
from infrastructure.persistence.sinh_vien.sinh_vien_repository import SinhVienRepository
from infrastructure.persistence.models import LopHocPhan, DangKyHocPhan

from unittest.mock import patch

# @pytest.mark.django_db(databases=['neon'])
class TestHuyDangKyHocPhanUseCase:
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
        return HuyDangKyHocPhanUseCase(
            mock_lhp_repo,
            mock_dkhp_repo,
            mock_tkb_repo,
            mock_lich_su_repo,
            mock_ky_phase_repo,
            mock_sinh_vien_repo
        )

    def test_execute_success(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_dkhp_repo, mock_tkb_repo, mock_lhp_repo):
        # Arrange
        sinh_vien_id = "sv-1"
        lop_hoc_phan_id = "lhp-1"
        hoc_ky_id = "hk-1"
        
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="dang_ky_hoc_phan")
        
        dang_ky = MagicMock(spec=DangKyHocPhan)
        dang_ky.id = "dk-1"
        dang_ky.trang_thai = "da_dang_ky"
        mock_dkhp_repo.find_by_sinh_vien_and_lop_hoc_phan.return_value = dang_ky
        
        # Act
        result = use_case.execute(sinh_vien_id, lop_hoc_phan_id, hoc_ky_id)
        
        # Assert
        assert result.success is True
        mock_tkb_repo.delete_by_dang_ky_id.assert_called_with("dk-1")
        mock_dkhp_repo.update_status.assert_called_with("dk-1", "da_huy")
        mock_lhp_repo.update_so_luong.assert_called_with(lop_hoc_phan_id, -1)

    def test_execute_fail_not_registered(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_dkhp_repo):
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="dang_ky_hoc_phan")
        mock_dkhp_repo.find_by_sinh_vien_and_lop_hoc_phan.return_value = None
        
        result = use_case.execute("sv-1", "lhp-1", "hk-1")
        
        assert result.success is False
        assert result.error_code == "REGISTRATION_NOT_FOUND"

    def test_execute_fail_invalid_status(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_dkhp_repo):
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="dang_ky_hoc_phan")
        
        dang_ky = MagicMock(spec=DangKyHocPhan)
        dang_ky.trang_thai = "da_huy"
        mock_dkhp_repo.find_by_sinh_vien_and_lop_hoc_phan.return_value = dang_ky
        
        result = use_case.execute("sv-1", "lhp-1", "hk-1")
        
        assert result.success is False
        assert result.error_code == "INVALID_STATUS"
