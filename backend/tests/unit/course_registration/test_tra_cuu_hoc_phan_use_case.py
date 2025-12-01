import unittest
from unittest.mock import Mock, MagicMock
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
        
        # Create mock LopHocPhan
        mock_lhp = MagicMock()
        mock_lhp.id = "lhp_id"
        mock_lhp.ma_lop = "COMP001_1"
        mock_lhp.so_luong_toi_da = 50
        
        # Mock mon_hoc
        mock_mon_hoc = MagicMock()
        mock_mon_hoc.id = "mh_id"
        mock_mon_hoc.ma_mon = "COMP001"
        mock_mon_hoc.ten_mon = "Test Subject"
        mock_mon_hoc.so_tin_chi = 3
        mock_mon_hoc.loai_mon = "chuyen_nganh"
        
        # Mock hoc_phan
        mock_hoc_phan = MagicMock()
        mock_hoc_phan.mon_hoc = mock_mon_hoc
        mock_lhp.hoc_phan = mock_hoc_phan
        
        # Mock giang_vien (OneToOne with Users)
        mock_user = MagicMock()
        mock_user.ho_ten = "Nguyen Van A"
        mock_gv = MagicMock()
        mock_gv.id = mock_user
        mock_lhp.giang_vien = mock_gv
        
        # Mock related sets
        mock_lhp.lichhocdinhky_set = MagicMock()
        mock_lhp.lichhocdinhky_set.all.return_value = []
        mock_lhp.dangkyhocphan_set = MagicMock()
        mock_lhp.dangkyhocphan_set.count.return_value = 5
        
        self.mock_repo.find_lop_hoc_phan_by_hoc_ky.return_value = [mock_lhp]

        # Act
        result = self.use_case.execute(hoc_ky_id)

        # Assert
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, list)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["maMon"], "COMP001")
        self.assertEqual(result.data[0]["tenMon"], "Test Subject")
        self.assertEqual(len(result.data[0]["danhSachLop"]), 1)
        self.assertEqual(result.data[0]["danhSachLop"][0]["giangVien"], "Nguyen Van A")
        self.mock_repo.find_lop_hoc_phan_by_hoc_ky.assert_called_once_with(hoc_ky_id)

    def test_execute_empty_result(self):
        # Arrange
        self.mock_repo.find_lop_hoc_phan_by_hoc_ky.return_value = []

        # Act
        result = self.use_case.execute("any_id")

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.data, [])

    def test_execute_failure(self):
        # Arrange
        self.mock_repo.find_lop_hoc_phan_by_hoc_ky.side_effect = Exception("DB Error")

        # Act
        result = self.use_case.execute("any_id")

        # Assert
        self.assertFalse(result.success)
        self.assertEqual(result.message, "DB Error")

if __name__ == '__main__':
    unittest.main()
