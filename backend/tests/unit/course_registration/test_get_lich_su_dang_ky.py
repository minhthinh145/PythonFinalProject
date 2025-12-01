import pytest
from unittest.mock import Mock, MagicMock
from application.course_registration.use_cases.get_lich_su_dang_ky_use_case import GetLichSuDangKyUseCase
from core.types import ServiceResult

class TestGetLichSuDangKyUseCase:
    @pytest.fixture
    def mock_lich_su_repo(self):
        return Mock()

    @pytest.fixture
    def use_case(self, mock_lich_su_repo):
        return GetLichSuDangKyUseCase(mock_lich_su_repo)

    def test_execute_success(self, use_case, mock_lich_su_repo):
        # Arrange
        sinh_vien_id = "sv1"
        hoc_ky_id = "hk1"
        
        mock_history = MagicMock()
        mock_history.chitietlichsudangky_set.all.return_value = [
            MagicMock(hanh_dong="dang_ky", thoi_gian="2023-01-01", dang_ky_hoc_phan=MagicMock(lop_hoc_phan=MagicMock(ma_lop="L01", ten_lop_hoc_phan="Lop 1"))),
            MagicMock(hanh_dong="huy_dang_ky", thoi_gian="2023-01-02", dang_ky_hoc_phan=MagicMock(lop_hoc_phan=MagicMock(ma_lop="L01", ten_lop_hoc_phan="Lop 1")))
        ]
        mock_lich_su_repo.find_by_sinh_vien_and_hoc_ky.return_value = mock_history

        # Act
        result = use_case.execute(sinh_vien_id, hoc_ky_id)

        # Assert
        assert result.success
        data = result.data
        # Both 'lichSu' and 'logs' keys exist (backward compat)
        assert 'lichSu' in data
        assert 'logs' in data
        assert len(data['lichSu']) == 2
        # Results sorted descending by thoi_gian, so newest (2023-01-02) first
        assert data['lichSu'][0]['hanhDong'] == "huy_dang_ky"
        assert data['lichSu'][1]['hanhDong'] == "dang_ky"

    def test_execute_no_history(self, use_case, mock_lich_su_repo):
        mock_lich_su_repo.find_by_sinh_vien_and_hoc_ky.return_value = None
        
        result = use_case.execute("sv1", "hk1")
        
        assert result.success
        assert result.data['lichSu'] == []
        assert result.data['logs'] == []  # backward compat

    def test_execute_missing_params(self, use_case):
        result = use_case.execute("", "hk1")
        assert not result.success
        assert result.error_code == "MISSING_PARAMS"
