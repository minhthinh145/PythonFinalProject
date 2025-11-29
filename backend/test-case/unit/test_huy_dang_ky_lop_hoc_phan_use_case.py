"""
Unit Tests for HuyDangKyLopHocPhanUseCase
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from application.course_registration.use_cases import HuyDangKyLopHocPhanUseCase
from application.course_registration.interfaces import (
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository,
    ILopHocPhanRepository
)
from application.enrollment.interfaces import IDotDangKyRepository

class TestHuyDangKyLopHocPhanUseCase:
    
    @pytest.fixture(autouse=True)
    def mock_transaction(self):
        with patch('django.db.transaction.atomic'):
            yield

    @pytest.fixture
    def mock_repos(self):
        return {
            'dang_ky_hp': Mock(spec=IDangKyHocPhanRepository),
            'dot_dang_ky': Mock(spec=IDotDangKyRepository),
            'dang_ky_tkb': Mock(spec=IDangKyTKBRepository),
            'lich_su': Mock(spec=ILichSuDangKyRepository),
            'lop_hoc_phan': Mock(spec=ILopHocPhanRepository)
        }

    @pytest.fixture
    def use_case(self, mock_repos):
        return HuyDangKyLopHocPhanUseCase(
            mock_repos['dang_ky_hp'],
            mock_repos['dot_dang_ky'],
            mock_repos['dang_ky_tkb'],
            mock_repos['lich_su'],
            mock_repos['lop_hoc_phan']
        )

    def test_execute_success(self, use_case, mock_repos):
        # Arrange
        user_id = "user-1"
        request_data = {"lopHocPhanId": "LHP1"}
        
        # 1. DangKy exists
        mock_dk = Mock(id="DK1", trang_thai="da_dang_ky")
        mock_dk.lop_hoc_phan.hoc_phan.id_hoc_ky = "HK1"
        mock_repos['dang_ky_hp'].find_by_sinh_vien_and_lop_hoc_phan.return_value = mock_dk
        
        # 2. DotDangKy active and not expired
        mock_dot = Mock(han_huy_den=datetime.now() + timedelta(days=1))
        mock_repos['dot_dang_ky'].find_active_dot_dang_ky.return_value = mock_dot
        
        # Act
        result = use_case.execute(request_data, user_id)
        
        # Assert
        assert result.success is True
        assert result.message == "Hủy đăng ký học phần thành công"
        mock_repos['dang_ky_hp'].update_status.assert_called_with("DK1", "da_huy")
        mock_repos['dang_ky_tkb'].delete_by_dang_ky_id.assert_called_with("DK1")
        mock_repos['lich_su'].upsert_and_log.assert_called_with(user_id, "HK1", "DK1", "huy_dang_ky")
        mock_repos['lop_hoc_phan'].update_so_luong.assert_called_with("LHP1", -1)

    def test_execute_fail_not_found(self, use_case, mock_repos):
        mock_repos['dang_ky_hp'].find_by_sinh_vien_and_lop_hoc_phan.return_value = None
        result = use_case.execute({"lopHocPhanId": "LHP1"}, "user-1")
        assert result.success is False
        assert result.error_code == "DANG_KY_NOT_FOUND"

    def test_execute_fail_already_cancelled(self, use_case, mock_repos):
        mock_dk = Mock(id="DK1", trang_thai="da_huy")
        mock_repos['dang_ky_hp'].find_by_sinh_vien_and_lop_hoc_phan.return_value = mock_dk
        result = use_case.execute({"lopHocPhanId": "LHP1"}, "user-1")
        assert result.success is False
        assert result.error_code == "ALREADY_CANCELLED"

    def test_execute_fail_past_deadline(self, use_case, mock_repos):
        mock_dk = Mock(id="DK1", trang_thai="da_dang_ky")
        mock_dk.lop_hoc_phan.hoc_phan.id_hoc_ky = "HK1"
        mock_repos['dang_ky_hp'].find_by_sinh_vien_and_lop_hoc_phan.return_value = mock_dk
        
        mock_dot = Mock(han_huy_den=datetime.now() - timedelta(days=1))
        mock_repos['dot_dang_ky'].find_active_dot_dang_ky.return_value = mock_dot
        
        result = use_case.execute({"lopHocPhanId": "LHP1"}, "user-1")
        assert result.success is False
        assert result.error_code == "PAST_CANCEL_DEADLINE"
