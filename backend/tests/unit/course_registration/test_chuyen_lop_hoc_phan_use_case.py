import unittest
from unittest.mock import Mock
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    django.setup()

import pytest
from unittest.mock import Mock, MagicMock
from application.course_registration.use_cases.chuyen_lop_hoc_phan_use_case import ChuyenLopHocPhanUseCase
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

# @pytest.mark.django_db(databases=['neon']) # Removed DB dependency
class TestChuyenLopHocPhanUseCase:
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
        return ChuyenLopHocPhanUseCase(
            mock_lhp_repo,
            mock_dkhp_repo,
            mock_tkb_repo,
            mock_lich_su_repo,
            mock_ky_phase_repo,
            mock_sinh_vien_repo
        )

    def test_execute_success(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_dkhp_repo, mock_lhp_repo, mock_tkb_repo):
        # Arrange
        sinh_vien_id = "sv-1"
        lop_cu_id = "lhp-old"
        lop_moi_id = "lhp-new"
        hoc_ky_id = "hk-1"
        
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="dang_ky_hoc_phan")
        
        # Old registration
        dang_ky_cu = MagicMock(spec=DangKyHocPhan)
        dang_ky_cu.id = "dk-old"
        dang_ky_cu.trang_thai = "da_dang_ky"
        mock_dkhp_repo.find_by_sinh_vien_and_lop_hoc_phan.return_value = dang_ky_cu
        
        # New class
        lop_moi = MagicMock(spec=LopHocPhan)
        lop_moi.so_luong_hien_tai = 10
        lop_moi.so_luong_toi_da = 50
        lop_moi.hoc_phan.mon_hoc_id = "mon-1"
        lop_moi.lichhocdinhky_set.all.return_value = []
        mock_lhp_repo.find_by_id.side_effect = lambda id: lop_moi if id == lop_moi_id else MagicMock(hoc_phan=MagicMock(mon_hoc_id="mon-1"))
        
        mock_tkb_repo.find_registered_lop_hoc_phans_by_hoc_ky.return_value = []
        mock_dkhp_repo.create.return_value = MagicMock(id="dk-new")
        
        # Act
        result = use_case.execute(sinh_vien_id, lop_cu_id, lop_moi_id, hoc_ky_id)
        
        # Assert
        assert result.success is True
        mock_dkhp_repo.update_status.assert_called_with("dk-old", "da_huy")
        mock_lhp_repo.update_so_luong.assert_any_call(lop_cu_id, -1)
        mock_lhp_repo.update_so_luong.assert_any_call(lop_moi_id, 1)
        mock_dkhp_repo.create.assert_called()

    def test_execute_fail_subject_mismatch(self, use_case, mock_sinh_vien_repo, mock_ky_phase_repo, mock_dkhp_repo, mock_lhp_repo):
        mock_sinh_vien_repo.get_by_id.return_value = MagicMock()
        mock_ky_phase_repo.get_current_phase.return_value = MagicMock(phase="dang_ky_hoc_phan")
        
        dang_ky_cu = MagicMock(spec=DangKyHocPhan)
        dang_ky_cu.trang_thai = "da_dang_ky"
        mock_dkhp_repo.find_by_sinh_vien_and_lop_hoc_phan.return_value = dang_ky_cu
        
        lop_moi = MagicMock(spec=LopHocPhan)
        lop_moi.so_luong_hien_tai = 10
        lop_moi.so_luong_toi_da = 50
        lop_moi.hoc_phan.mon_hoc_id = "mon-2"
        
        lop_cu = MagicMock(spec=LopHocPhan)
        lop_cu.hoc_phan.mon_hoc_id = "mon-1"
        
        mock_lhp_repo.find_by_id.side_effect = lambda id: lop_moi if id == "lhp-new" else lop_cu
        
        result = use_case.execute("sv-1", "lhp-old", "lhp-new", "hk-1")
        
        assert result.success is False
        assert result.error_code == "SUBJECT_MISMATCH"
