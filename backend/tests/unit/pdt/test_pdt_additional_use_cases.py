"""
Additional tests for PDT module use cases
Tests: DuyetDeXuatHocPhan, TuChoiDeXuatHocPhan, GetDanhSachKhoa, GetDeXuatHocPhan
"""
import pytest
from unittest.mock import MagicMock, Mock

from application.pdt.use_cases.duyet_de_xuat_hoc_phan_use_case import DuyetDeXuatHocPhanUseCase
from application.pdt.use_cases.tu_choi_de_xuat_hoc_phan_use_case import TuChoiDeXuatHocPhanUseCase
from application.pdt.use_cases.get_danh_sach_khoa_use_case import GetDanhSachKhoaUseCase
from application.pdt.use_cases.get_de_xuat_hoc_phan_use_case import GetDeXuatHocPhanUseCase


# ==================== FIXTURES ====================

@pytest.fixture
def mock_de_xuat_repo():
    return MagicMock()


@pytest.fixture
def mock_khoa_repo():
    return MagicMock()


# ==================== DuyetDeXuatHocPhanUseCase Tests ====================

class TestDuyetDeXuatHocPhanUseCase:
    """Tests for DuyetDeXuatHocPhanUseCase"""
    
    def test_duyet_success(self, mock_de_xuat_repo):
        """Test successful proposal approval"""
        # Arrange
        mock_de_xuat_repo.approve_proposal.return_value = True
        
        use_case = DuyetDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("dx-001")
        
        # Assert
        assert result.success is True
        mock_de_xuat_repo.approve_proposal.assert_called_once_with("dx-001")
    
    def test_duyet_missing_id(self, mock_de_xuat_repo):
        """Test approval with missing proposal ID"""
        # Arrange
        use_case = DuyetDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("")
        
        # Assert
        assert result.success is False
        assert result.error_code == "MISSING_PARAMS"
    
    def test_duyet_not_found(self, mock_de_xuat_repo):
        """Test approval when proposal not found"""
        # Arrange
        mock_de_xuat_repo.approve_proposal.return_value = False
        
        use_case = DuyetDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("dx-invalid")
        
        # Assert
        assert result.success is False
        assert result.error_code == "NOT_FOUND"


# ==================== TuChoiDeXuatHocPhanUseCase Tests ====================

class TestTuChoiDeXuatHocPhanUseCase:
    """Tests for TuChoiDeXuatHocPhanUseCase"""
    
    def test_tu_choi_success(self, mock_de_xuat_repo):
        """Test successful proposal rejection"""
        # Arrange
        mock_de_xuat_repo.reject_proposal.return_value = True
        
        use_case = TuChoiDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("dx-001", "Không phù hợp với chương trình")
        
        # Assert
        assert result.success is True
    
    def test_tu_choi_missing_id(self, mock_de_xuat_repo):
        """Test rejection with missing proposal ID"""
        # Arrange
        use_case = TuChoiDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("", "Lý do")
        
        # Assert
        assert result.success is False
    
    def test_tu_choi_not_found(self, mock_de_xuat_repo):
        """Test rejection when proposal not found"""
        # Arrange
        mock_de_xuat_repo.reject_proposal.return_value = False
        
        use_case = TuChoiDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("dx-invalid", "Lý do")
        
        # Assert
        assert result.success is False


# ==================== GetDanhSachKhoaUseCase Tests ====================

class TestGetDanhSachKhoaUseCase:
    """Tests for GetDanhSachKhoaUseCase"""
    
    def test_get_danh_sach_success(self, mock_khoa_repo):
        """Test successful retrieval of departments"""
        # Arrange
        mock_khoa_1 = MagicMock()
        mock_khoa_1.id = "khoa-001"
        mock_khoa_1.ma_khoa = "CNTT"
        mock_khoa_1.ten_khoa = "Công nghệ thông tin"
        
        mock_khoa_2 = MagicMock()
        mock_khoa_2.id = "khoa-002"
        mock_khoa_2.ma_khoa = "DTVT"
        mock_khoa_2.ten_khoa = "Điện tử viễn thông"
        
        mock_khoa_repo.get_all.return_value = [mock_khoa_1, mock_khoa_2]
        
        use_case = GetDanhSachKhoaUseCase(mock_khoa_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result["isSuccess"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["maKhoa"] == "CNTT"
    
    def test_get_danh_sach_empty(self, mock_khoa_repo):
        """Test with no departments"""
        # Arrange
        mock_khoa_repo.get_all.return_value = []
        
        use_case = GetDanhSachKhoaUseCase(mock_khoa_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result["isSuccess"] is True
        assert result["data"] == []


# ==================== GetDeXuatHocPhanUseCase Tests ====================

class TestGetDeXuatHocPhanUseCase:
    """Tests for GetDeXuatHocPhanUseCase"""
    
    def test_get_de_xuat_success(self, mock_de_xuat_repo):
        """Test successful retrieval of proposals"""
        # Arrange
        mock_de_xuat_repo.get_pending_proposals.return_value = [
            {
                "id": "dx-001",
                "ten_mon_hoc": "Toán cao cấp",
                "so_lop": 2,
                "trang_thai": "cho_duyet"
            },
            {
                "id": "dx-002",
                "ten_mon_hoc": "Vật lý",
                "so_lop": 1,
                "trang_thai": "da_duyet"
            }
        ]
        
        use_case = GetDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert len(result.data) == 2
    
    def test_get_de_xuat_empty(self, mock_de_xuat_repo):
        """Test with no proposals"""
        # Arrange
        mock_de_xuat_repo.get_pending_proposals.return_value = []
        
        use_case = GetDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert result.data == []
    
    def test_get_de_xuat_with_data(self, mock_de_xuat_repo):
        """Test retrieval with proposals data"""
        # Arrange
        mock_de_xuat_repo.get_pending_proposals.return_value = [
            {
                "id": "dx-001",
                "ten_mon_hoc": "Toán cao cấp",
                "so_lop": 2,
                "trang_thai": "cho_duyet"
            }
        ]
        
        use_case = GetDeXuatHocPhanUseCase(mock_de_xuat_repo)
        
        # Act
        result = use_case.execute()
        
        # Assert
        assert result.success is True
        assert len(result.data) == 1
