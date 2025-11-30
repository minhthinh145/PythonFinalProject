import unittest
from unittest.mock import Mock
from application.pdt.use_cases.get_phases_by_hoc_ky_use_case import GetPhasesByHocKyUseCase
from application.enrollment.interfaces.repositories import IKyPhaseRepository

class TestGetPhasesByHocKyUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_repo = Mock(spec=IKyPhaseRepository)
        self.use_case = GetPhasesByHocKyUseCase(self.mock_repo)

    def test_execute_success(self):
        # Arrange
        hoc_ky_id = "test_hoc_ky_id"
        mock_phase = Mock()
        mock_phase.id = "phase_id"
        mock_phase.phase = "ghi_danh"
        mock_phase.start_at = "2023-01-01"
        mock_phase.end_at = "2023-01-10"
        mock_phase.is_enabled = True
        
        self.mock_repo.find_by_hoc_ky.return_value = [mock_phase]

        # Act
        result = self.use_case.execute(hoc_ky_id)

        # Assert
        self.assertTrue(result.success)
        self.assertIn("phases", result.data)
        self.assertEqual(len(result.data["phases"]), 1)
        self.assertEqual(result.data["phases"][0]["phase"], "ghi_danh")
        self.mock_repo.find_by_hoc_ky.assert_called_once_with(hoc_ky_id)

    def test_execute_failure(self):
        # Arrange
        self.mock_repo.find_by_hoc_ky.side_effect = Exception("DB Error")

        # Act
        result = self.use_case.execute("any_id")

        # Assert
        self.assertFalse(result.success)
        self.assertEqual(result.message, "DB Error")

if __name__ == '__main__':
    unittest.main()
