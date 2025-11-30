
import pytest
from unittest.mock import Mock
from application.course_registration.use_cases.check_phase_dang_ky_use_case import CheckPhaseDangKyUseCase
from application.enrollment.interfaces import IKyPhaseRepository
from infrastructure.persistence.models import KyPhase

class TestCheckPhaseDangKyUseCase:
    @pytest.fixture
    def mock_ky_phase_repo(self):
        return Mock(spec=IKyPhaseRepository)

    @pytest.fixture
    def use_case(self, mock_ky_phase_repo):
        return CheckPhaseDangKyUseCase(mock_ky_phase_repo)

    def test_execute_success(self, use_case, mock_ky_phase_repo):
        # Arrange
        hoc_ky_id = "test-hoc-ky-id"
        mock_phase = Mock(spec=KyPhase)
        mock_phase.phase = "dang_ky_hoc_phan"
        mock_ky_phase_repo.get_current_phase.return_value = mock_phase

        # Act
        result = use_case.execute(hoc_ky_id)

        # Assert
        assert result.success is True
        assert result.message == "Phase đăng ký học phần đang mở"
        mock_ky_phase_repo.get_current_phase.assert_called_once_with(hoc_ky_id)

    def test_execute_no_active_phase(self, use_case, mock_ky_phase_repo):
        # Arrange
        hoc_ky_id = "test-hoc-ky-id"
        mock_ky_phase_repo.get_current_phase.return_value = None

        # Act
        result = use_case.execute(hoc_ky_id)

        # Assert
        assert result.success is False
        assert result.message == "Chưa có phase nào đang mở"
        assert result.error_code == "NO_ACTIVE_PHASE"

    def test_execute_wrong_phase(self, use_case, mock_ky_phase_repo):
        # Arrange
        hoc_ky_id = "test-hoc-ky-id"
        mock_phase = Mock(spec=KyPhase)
        mock_phase.phase = "ghi_danh" # Not dang_ky_hoc_phan
        mock_ky_phase_repo.get_current_phase.return_value = mock_phase

        # Act
        result = use_case.execute(hoc_ky_id)

        # Assert
        assert result.success is False
        assert "Chưa đến phase đăng ký học phần" in result.message
        assert result.error_code == "WRONG_PHASE"
