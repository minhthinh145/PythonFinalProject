"""
Comprehensive tests for Enrollment module use cases
Tests: GetDanhSachDaGhiDanh, GetHocKy, GetMonHocGhiDanh, GhiDanhMonHoc, HuyGhiDanhMonHoc
"""
import pytest
from unittest.mock import MagicMock, Mock
from datetime import date

from application.enrollment.use_cases.get_danh_sach_da_ghi_danh_use_case import GetDanhSachDaGhiDanhUseCase
from application.enrollment.use_cases.get_hoc_ky_use_case import GetHocKyUseCase
from application.enrollment.use_cases.get_mon_hoc_ghi_danh_use_case import GetMonHocGhiDanhUseCase
from application.enrollment.use_cases.ghi_danh_mon_hoc_use_case import GhiDanhMonHocUseCase
from application.enrollment.use_cases.huy_ghi_danh_mon_hoc_use_case import HuyGhiDanhMonHocUseCase


# ==================== FIXTURES ====================

@pytest.fixture
def mock_ghi_danh_repo():
    return MagicMock()


@pytest.fixture
def mock_hoc_ky_repo():
    return MagicMock()


@pytest.fixture
def mock_hoc_phan_repo():
    return MagicMock()


# ==================== HuyGhiDanhMonHocUseCase Tests ====================

class TestHuyGhiDanhMonHocUseCase:
    """Tests for HuyGhiDanhMonHocUseCase"""
    
    def test_huy_ghi_danh_success(self, mock_ghi_danh_repo):
        """Test successful enrollment cancellation"""
        # Arrange
        use_case = HuyGhiDanhMonHocUseCase(mock_ghi_danh_repo)
        request_data = {"ghiDanhIds": ["gd-001", "gd-002"]}
        
        # Act
        result = use_case.execute(request_data, "user-001")
        
        # Assert
        assert result.success is True
        assert "thành công" in result.message
        mock_ghi_danh_repo.delete_many.assert_called_once_with(["gd-001", "gd-002"])
    
    def test_huy_ghi_danh_invalid_input_none(self, mock_ghi_danh_repo):
        """Test cancellation with None ghiDanhIds"""
        # Arrange
        use_case = HuyGhiDanhMonHocUseCase(mock_ghi_danh_repo)
        request_data = {"ghiDanhIds": None}
        
        # Act
        result = use_case.execute(request_data, "user-001")
        
        # Assert
        assert result.success is False
        assert result.error_code == "INVALID_INPUT"
    
    def test_huy_ghi_danh_invalid_input_not_list(self, mock_ghi_danh_repo):
        """Test cancellation with non-list ghiDanhIds"""
        # Arrange
        use_case = HuyGhiDanhMonHocUseCase(mock_ghi_danh_repo)
        request_data = {"ghiDanhIds": "not_a_list"}
        
        # Act
        result = use_case.execute(request_data, "user-001")
        
        # Assert
        assert result.success is False
        assert result.error_code == "INVALID_INPUT"
    
    def test_huy_ghi_danh_empty_list(self, mock_ghi_danh_repo):
        """Test cancellation with empty ghiDanhIds list"""
        # Arrange
        use_case = HuyGhiDanhMonHocUseCase(mock_ghi_danh_repo)
        request_data = {"ghiDanhIds": []}
        
        # Act
        result = use_case.execute(request_data, "user-001")
        
        # Assert
        # Empty list should be treated as invalid
        assert result.success is False


# ==================== GetHocKyUseCase Tests ====================

class TestGetHocKyUseCase:
    """Tests for GetHocKyUseCase"""
    
    def test_get_hoc_ky_success(self, mock_hoc_ky_repo):
        """Test successful retrieval of hoc ky list"""
        # Arrange
        mock_nien_khoa = MagicMock()
        mock_nien_khoa.id = "nk-001"
        mock_nien_khoa.ten_nien_khoa = "2023-2024"
        
        mock_hoc_ky_1 = MagicMock()
        mock_hoc_ky_1.id = "hk-001"
        mock_hoc_ky_1.ten_hoc_ky = "Học kỳ 1"
        mock_hoc_ky_1.ma_hoc_ky = "HK1"
        mock_hoc_ky_1.ngay_bat_dau = date(2023, 9, 1)
        mock_hoc_ky_1.ngay_ket_thuc = date(2024, 1, 15)
        mock_hoc_ky_1.id_nien_khoa = mock_nien_khoa
        
        mock_hoc_ky_2 = MagicMock()
        mock_hoc_ky_2.id = "hk-002"
        mock_hoc_ky_2.ten_hoc_ky = "Học kỳ 2"
        mock_hoc_ky_2.ma_hoc_ky = "HK2"
        mock_hoc_ky_2.ngay_bat_dau = date(2024, 2, 1)
        mock_hoc_ky_2.ngay_ket_thuc = date(2024, 6, 15)
        mock_hoc_ky_2.id_nien_khoa = mock_nien_khoa
        
        mock_hoc_ky_repo.get_all_hoc_ky.return_value = [mock_hoc_ky_1, mock_hoc_ky_2]
        
        use_case = GetHocKyUseCase(mock_hoc_ky_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert len(result.data) == 1  # Grouped by NienKhoa
        assert result.data[0]['tenNienKhoa'] == "2023-2024"
        assert len(result.data[0]['hocKy']) == 2
    
    def test_get_hoc_ky_empty(self, mock_hoc_ky_repo):
        """Test with no hoc ky data"""
        # Arrange
        mock_hoc_ky_repo.get_all_hoc_ky.return_value = []
        
        use_case = GetHocKyUseCase(mock_hoc_ky_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert result.data == []
    
    def test_get_hoc_ky_exception(self, mock_hoc_ky_repo):
        """Test exception handling"""
        # Arrange
        mock_hoc_ky_repo.get_all_hoc_ky.side_effect = Exception("Database error")
        
        use_case = GetHocKyUseCase(mock_hoc_ky_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is False


# ==================== GetDanhSachDaGhiDanhUseCase Tests ====================

class TestGetDanhSachDaGhiDanhUseCase:
    """Tests for GetDanhSachDaGhiDanhUseCase"""
    
    def test_get_danh_sach_success(self, mock_ghi_danh_repo):
        """Test successful retrieval of enrolled subjects"""
        # Arrange - Mock complete ghi_danh objects
        mock_mon_hoc = MagicMock()
        mock_mon_hoc.ma_mon = "COMP1325"
        mock_mon_hoc.ten_mon = "Toán"
        mock_mon_hoc.so_tin_chi = 3
        mock_mon_hoc.khoa.ten_khoa = "CNTT"
        mock_mon_hoc.dexuathocphan_set.all.return_value = []
        
        mock_hoc_phan = MagicMock()
        mock_hoc_phan.id = "hp-001"
        mock_hoc_phan.mon_hoc = mock_mon_hoc
        
        mock_ghi_danh = MagicMock()
        mock_ghi_danh.id = "gd-001"
        mock_ghi_danh.hoc_phan = mock_hoc_phan
        
        mock_ghi_danh_repo.find_by_sinh_vien.return_value = [mock_ghi_danh]
        
        use_case = GetDanhSachDaGhiDanhUseCase(mock_ghi_danh_repo)
        
        # Act
        result = use_case.execute("sv-001")
        
        # Assert
        assert result.success is True
        assert len(result.data) == 1
    
    def test_get_danh_sach_empty(self, mock_ghi_danh_repo):
        """Test with no enrolled subjects"""
        # Arrange
        mock_ghi_danh_repo.find_by_sinh_vien.return_value = []
        
        use_case = GetDanhSachDaGhiDanhUseCase(mock_ghi_danh_repo)
        
        # Act
        result = use_case.execute("sv-001")
        
        # Assert
        assert result.success is True
        assert result.data == []


# ==================== GetMonHocGhiDanhUseCase Tests ====================

class TestGetMonHocGhiDanhUseCase:
    """Tests for GetMonHocGhiDanhUseCase"""
    
    def test_get_mon_hoc_with_hoc_ky_id(self, mock_hoc_ky_repo, mock_hoc_phan_repo):
        """Test with provided hoc_ky_id"""
        # Arrange
        mock_mon_hoc = MagicMock()
        mock_mon_hoc.ma_mon = "COMP1325"
        mock_mon_hoc.ten_mon = "Toán cao cấp"
        mock_mon_hoc.so_tin_chi = 4
        mock_mon_hoc.khoa.ten_khoa = "CNTT"
        mock_mon_hoc.dexuathocphan_set.all.return_value = []
        
        mock_hoc_phan = MagicMock()
        mock_hoc_phan.id = "hp-001"
        mock_hoc_phan.mon_hoc = mock_mon_hoc
        
        mock_hoc_phan_repo.find_all_open.return_value = [mock_hoc_phan]
        
        use_case = GetMonHocGhiDanhUseCase(mock_hoc_ky_repo, mock_hoc_phan_repo)
        
        # Act
        result = use_case.execute("hk-001")
        
        # Assert
        assert result.success is True
    
    def test_get_mon_hoc_without_hoc_ky_id(self, mock_hoc_ky_repo, mock_hoc_phan_repo):
        """Test without provided hoc_ky_id - uses current hoc_ky"""
        # Arrange
        mock_hoc_ky = MagicMock()
        mock_hoc_ky.id = "hk-current"
        mock_hoc_ky_repo.get_current_hoc_ky.return_value = mock_hoc_ky
        mock_hoc_phan_repo.find_all_open.return_value = []
        
        use_case = GetMonHocGhiDanhUseCase(mock_hoc_ky_repo, mock_hoc_phan_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
    
    def test_get_mon_hoc_no_current_hoc_ky(self, mock_hoc_ky_repo, mock_hoc_phan_repo):
        """Test when no current hoc_ky exists"""
        # Arrange
        mock_hoc_ky_repo.get_current_hoc_ky.return_value = None
        
        use_case = GetMonHocGhiDanhUseCase(mock_hoc_ky_repo, mock_hoc_phan_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is False
        assert result.error_code == "HOC_KY_HIEN_HANH_NOT_FOUND"


# ==================== GhiDanhMonHocUseCase Tests ====================

class TestGhiDanhMonHocUseCase:
    """Tests for GhiDanhMonHocUseCase"""
    
    def test_ghi_danh_success(self, mock_hoc_phan_repo, mock_ghi_danh_repo):
        """Test successful enrollment"""
        # Arrange
        mock_hoc_phan = MagicMock()
        mock_hoc_phan.trang_thai_mo = True
        mock_hoc_phan_repo.find_by_id.return_value = mock_hoc_phan
        mock_ghi_danh_repo.is_already_registered.return_value = False
        
        use_case = GhiDanhMonHocUseCase(mock_hoc_phan_repo, mock_ghi_danh_repo)
        request = {"monHocId": "mh-001"}
        
        # Act
        result = use_case.execute(request, "sv-001")
        
        # Assert
        assert result.success is True
        mock_ghi_danh_repo.create.assert_called_once()
    
    def test_ghi_danh_hoc_phan_not_found(self, mock_hoc_phan_repo, mock_ghi_danh_repo):
        """Test when hoc_phan not found"""
        # Arrange
        mock_hoc_phan_repo.find_by_id.return_value = None
        
        use_case = GhiDanhMonHocUseCase(mock_hoc_phan_repo, mock_ghi_danh_repo)
        request = {"monHocId": "mh-invalid"}
        
        # Act
        result = use_case.execute(request, "sv-001")
        
        # Assert
        assert result.success is False
        assert result.error_code == "HOC_PHAN_NOT_FOUND"
    
    def test_ghi_danh_hoc_phan_closed(self, mock_hoc_phan_repo, mock_ghi_danh_repo):
        """Test when hoc_phan is closed"""
        # Arrange
        mock_hoc_phan = MagicMock()
        mock_hoc_phan.trang_thai_mo = False
        mock_hoc_phan_repo.find_by_id.return_value = mock_hoc_phan
        
        use_case = GhiDanhMonHocUseCase(mock_hoc_phan_repo, mock_ghi_danh_repo)
        request = {"monHocId": "mh-001"}
        
        # Act
        result = use_case.execute(request, "sv-001")
        
        # Assert
        assert result.success is False
        assert result.error_code == "HOC_PHAN_CLOSED"
    
    def test_ghi_danh_already_registered(self, mock_hoc_phan_repo, mock_ghi_danh_repo):
        """Test when already registered"""
        # Arrange
        mock_hoc_phan = MagicMock()
        mock_hoc_phan.trang_thai_mo = True
        mock_hoc_phan_repo.find_by_id.return_value = mock_hoc_phan
        mock_ghi_danh_repo.is_already_registered.return_value = True
        
        use_case = GhiDanhMonHocUseCase(mock_hoc_phan_repo, mock_ghi_danh_repo)
        request = {"monHocId": "mh-001"}
        
        # Act
        result = use_case.execute(request, "sv-001")
        
        # Assert
        assert result.success is False
        assert result.error_code == "ALREADY_REGISTERED"
