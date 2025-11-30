import pytest
from unittest.mock import MagicMock
from application.pdt.use_cases.create_bulk_ky_phase_use_case import CreateBulkKyPhaseUseCase

class TestCreateBulkKyPhaseUseCase:
    @pytest.fixture
    def mock_ky_phase_repo(self):
        return MagicMock()

    @pytest.fixture
    def mock_hoc_ky_repo(self):
        return MagicMock()

    @pytest.fixture
    def mock_dot_dang_ky_repo(self):
        return MagicMock()

    @pytest.fixture
    def use_case(self, mock_ky_phase_repo, mock_hoc_ky_repo, mock_dot_dang_ky_repo):
        return CreateBulkKyPhaseUseCase(mock_ky_phase_repo, mock_hoc_ky_repo, mock_dot_dang_ky_repo)

    def test_execute_success(self, use_case, mock_ky_phase_repo):
        # Arrange
        data = {
            "hocKyId": "hk1",
            "hocKyStartAt": "2023-10-01",
            "hocKyEndAt": "2024-02-01",
            "phases": [
                {"phase": "ghi_danh", "startAt": "2023-10-01", "endAt": "2023-10-15"},
                {"phase": "dang_ky_hoc_phan", "startAt": "2023-10-16", "endAt": "2023-10-31"}
            ]
        }
        mock_ky_phase_repo.create_bulk.return_value = [MagicMock(), MagicMock()]

        # Act
        result = use_case.execute(data)

        # Assert
        assert result.success
        mock_ky_phase_repo.create_bulk.assert_called_once()
        args, _ = mock_ky_phase_repo.create_bulk.call_args
        # Check mapped structure
        assert args[0][0]['tenPhase'] == "ghi_danh"
        assert args[1] == "hk1"

    def test_execute_missing_params(self, use_case):
        result = use_case.execute({})
        assert not result.success
        assert result.error_code == "MISSING_PARAMS"

    def test_execute_empty_phases(self, use_case):
        result = use_case.execute({"hocKyId": "hk1", "phases": []})
        assert not result.success
        assert result.error_code == "MISSING_PARAMS"
