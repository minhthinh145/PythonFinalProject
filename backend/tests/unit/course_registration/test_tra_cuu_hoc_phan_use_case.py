import unittest
from unittest.mock import Mock
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    django.setup()

from application.course_registration.use_cases.tra_cuu_hoc_phan_use_case import TraCuuHocPhanUseCase
from application.enrollment.interfaces.repositories import IHocPhanRepository

class TestTraCuuHocPhanUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_repo = Mock(spec=IHocPhanRepository)
        self.use_case = TraCuuHocPhanUseCase(self.mock_repo)

    def test_execute_success(self):
        # Arrange
        hoc_ky_id = "test_hoc_ky_id"
        mock_hoc_phan = Mock()
        mock_hoc_phan.id = "hp_id"
        mock_hoc_phan.ten_hoc_phan = "Test Subject"
        mock_hoc_phan.so_lop = 2
        mock_hoc_phan.trang_thai_mo = True
        
        mock_mon_hoc = Mock()
        mock_mon_hoc.ma_mon = "HP001"
        mock_mon_hoc.so_tin_chi = 3
        mock_hoc_phan.mon_hoc = mock_mon_hoc
        
        self.mock_repo.find_all_open.return_value = [mock_hoc_phan]

        # Act
        result = self.use_case.execute(hoc_ky_id)

        # Assert
        self.assertTrue(result.success)
        self.assertIn("hocPhan", result.data)
        self.assertEqual(len(result.data["hocPhan"]), 1)
        self.assertEqual(result.data["hocPhan"][0]["maHocPhan"], "HP001")
        self.mock_repo.find_all_open.assert_called_once_with(hoc_ky_id)

    def test_execute_failure(self):
        # Arrange
        self.mock_repo.find_all_open.side_effect = Exception("DB Error")

        # Act
        result = self.use_case.execute("any_id")

        # Assert
        self.assertFalse(result.success)
        self.assertEqual(result.message, "DB Error")

if __name__ == '__main__':
    unittest.main()
