import unittest
from unittest.mock import Mock
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    django.setup()

from application.course_registration.use_cases.get_chi_tiet_hoc_phi_use_case import GetChiTietHocPhiUseCase
from application.course_registration.interfaces.repositories import IHocPhiRepository

class TestGetChiTietHocPhiUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_repo = Mock(spec=IHocPhiRepository)
        self.use_case = GetChiTietHocPhiUseCase(self.mock_repo)

    def test_execute_success(self):
        # Arrange
        sinh_vien_id = "sv_id"
        hoc_ky_id = "hk_id"
        
        mock_hoc_phi = Mock()
        mock_hoc_phi.tong_hoc_phi = 5000000
        mock_hoc_phi.trang_thai_thanh_toan = "CHUA_THANH_TOAN"
        mock_hoc_phi.so_tin_chi = 15
        mock_hoc_phi.chinh_sach = None  # No policy
        
        # Mock mon_hoc
        mock_mon_hoc = Mock()
        mock_mon_hoc.ma_mon = "MH001"
        mock_mon_hoc.ten_mon = "Subject 1"
        
        # Mock hoc_phan
        mock_hoc_phan = Mock()
        mock_hoc_phan.mon_hoc = mock_mon_hoc
        
        # Mock lop_hoc_phan
        mock_lhp = Mock()
        mock_lhp.ma_lop = "LHP001"
        mock_lhp.hoc_phan = mock_hoc_phan
        
        # Mock chi tiet (chitiethocphi_set, not chi_tiet_hoc_phi_set)
        mock_detail_1 = Mock()
        mock_detail_1.lop_hoc_phan = mock_lhp
        mock_detail_1.so_tin_chi = 3
        mock_detail_1.phi_tin_chi = 500000
        mock_detail_1.thanh_tien = 1500000
        
        mock_hoc_phi.chitiethocphi_set.all.return_value = [mock_detail_1]
        
        self.mock_repo.get_hoc_phi_by_sinh_vien.return_value = mock_hoc_phi

        # Act
        result = self.use_case.execute(sinh_vien_id, hoc_ky_id)

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.data["tongHocPhi"], 5000000)
        self.assertEqual(len(result.data["chiTiet"]), 1)
        self.assertEqual(result.data["chiTiet"][0]["maLop"], "LHP001")

    def test_execute_not_found(self):
        # Arrange
        self.mock_repo.get_hoc_phi_by_sinh_vien.return_value = None

        # Act
        result = self.use_case.execute("sv_id", "hk_id")

        # Assert
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "HOC_PHI_NOT_FOUND")

if __name__ == '__main__':
    unittest.main()
