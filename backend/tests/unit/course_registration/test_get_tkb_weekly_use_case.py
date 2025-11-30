import pytest
from unittest.mock import MagicMock
from datetime import date, datetime
from application.course_registration.use_cases.get_tkb_weekly_use_case import GetTKBWeeklyUseCase

class TestGetTKBWeeklyUseCase:
    @pytest.fixture
    def mock_dang_ky_repo(self):
        return MagicMock()

    @pytest.fixture
    def use_case(self, mock_dang_ky_repo):
        return GetTKBWeeklyUseCase(mock_dang_ky_repo)

    def test_execute_success(self, use_case, mock_dang_ky_repo):
        # Arrange
        sinh_vien_id = "sv1"
        hoc_ky_id = "hk1"
        date_start = date(2023, 10, 23) # Monday
        date_end = date(2023, 10, 29)   # Sunday

        # Mock registered class
        mock_reg = MagicMock()
        mock_reg.lop_hoc_phan.id = "lhp1"
        mock_reg.lop_hoc_phan.ma_lop = "LHP001"
        mock_reg.lop_hoc_phan.hoc_phan.mon_hoc.ma_mon = "MH001"
        mock_reg.lop_hoc_phan.hoc_phan.mon_hoc.ten_mon = "Subject 1"
        mock_reg.lop_hoc_phan.hoc_phan.ten_hoc_phan = "Subject 1 - Class 1"
        mock_reg.lop_hoc_phan.giang_vien.users.ho_ten = "Teacher A"

        # Mock schedule: Monday (2), periods 1-3
        mock_schedule = MagicMock()
        mock_schedule.thu = 2
        mock_schedule.tiet_bat_dau = 1
        mock_schedule.tiet_ket_thuc = 3
        mock_schedule.phong.id = "p1"
        mock_schedule.phong.ma_phong = "A101"
        
        # Configure mock to return list of schedules (Django related manager)
        # In the use case we iterate: for lich in lop.lichhocdinhky_set.all()
        # So we need to mock the related set.
        mock_reg.lop_hoc_phan.lichhocdinhky_set.all.return_value = [mock_schedule]

        mock_dang_ky_repo.find_by_sinh_vien_and_hoc_ky.return_value = [mock_reg]

        # Act
        result = use_case.execute(sinh_vien_id, hoc_ky_id, date_start, date_end)

        # Assert
        assert result.success
        data = result.data
        assert len(data) == 1
        item = data[0]
        assert item['thu'] == 2
        assert item['tiet_bat_dau'] == 1
        assert item['tiet_ket_thuc'] == 3
        assert item['phong']['ma_phong'] == "A101"
        assert item['ngay_hoc'] == "2023-10-23" # Monday

    def test_execute_no_registration(self, use_case, mock_dang_ky_repo):
        mock_dang_ky_repo.find_by_sinh_vien_and_hoc_ky.return_value = []
        result = use_case.execute("sv1", "hk1", date(2023, 10, 23), date(2023, 10, 29))
        assert result.success
        assert result.data == []

    def test_execute_missing_params(self, use_case):
        result = use_case.execute("", "hk1", date(2023, 10, 23), date(2023, 10, 29))
        assert not result.success
        assert result.error_code == "MISSING_PARAMS"
