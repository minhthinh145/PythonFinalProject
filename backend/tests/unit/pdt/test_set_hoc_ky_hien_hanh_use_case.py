import pytest
from unittest.mock import MagicMock
from application.pdt.use_cases.set_hoc_ky_hien_hanh_use_case import SetHocKyHienHanhUseCase

class TestSetHocKyHienHanhUseCase:
    @pytest.fixture
    def mock_hoc_ky_repo(self):
        return MagicMock()

    @pytest.fixture
    def use_case(self, mock_hoc_ky_repo):
        return SetHocKyHienHanhUseCase(mock_hoc_ky_repo)

    def test_execute_success(self, use_case, mock_hoc_ky_repo):
        # Arrange
        hoc_ky_id = "hk1"
        mock_hoc_ky = MagicMock()
        mock_hoc_ky.id = hoc_ky_id
        mock_hoc_ky_repo.find_by_id.return_value = mock_hoc_ky

        # Act
        result = use_case.execute(hoc_ky_id)

        # Assert
        assert result.success
        mock_hoc_ky_repo.set_current_semester.assert_called_once_with(hoc_ky_id)

    def test_execute_missing_param(self, use_case):
        result = use_case.execute("")
        assert not result.success
        assert result.error_code == "MISSING_PARAMS"

    def test_execute_not_found(self, use_case, mock_hoc_ky_repo):
        mock_hoc_ky_repo.find_by_id.return_value = None
        result = use_case.execute("invalid_id")
        assert not result.success
        assert result.error_code == "NOT_FOUND"
