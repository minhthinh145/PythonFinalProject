"""
Additional tests for TK (Trưởng Khoa) module use cases
Tests: DuyetDeXuatHocPhanByTK, TuChoiDeXuatHocPhanByTK
"""
import pytest
from unittest.mock import MagicMock

from application.tk.use_cases.duyet_de_xuat_use_case import DuyetDeXuatHocPhanByTKUseCase
from application.tk.use_cases.tu_choi_de_xuat_use_case import TuChoiDeXuatHocPhanByTKUseCase


# ==================== FIXTURES ====================

@pytest.fixture
def mock_tk_repo():
    return MagicMock()


@pytest.fixture
def mock_de_xuat_repo():
    return MagicMock()


@pytest.fixture
def mock_truong_khoa():
    """Mock truong khoa data"""
    return {
        "id": "tk-001",
        "user_id": "user-001",
        "khoa_id": "khoa-001",
        "ho_ten": "Nguyễn Văn TK"
    }


@pytest.fixture
def mock_de_xuat():
    """Mock de xuat data"""
    return {
        "id": "dx-001",
        "khoa_id": "khoa-001",
        "mon_hoc_id": "mh-001",
        "so_lop": 2,
        "trang_thai": "cho_duyet"
    }


# ==================== DuyetDeXuatHocPhanByTKUseCase Tests ====================

class TestDuyetDeXuatHocPhanByTKUseCase:
    """Tests for DuyetDeXuatHocPhanByTKUseCase"""
    
    def test_duyet_success(self, mock_tk_repo, mock_de_xuat_repo, mock_truong_khoa, mock_de_xuat):
        """Test successful approval by TK"""
        # Arrange
        mock_tk_repo.find_by_user_id.return_value = mock_truong_khoa
        mock_de_xuat_repo.find_by_id.return_value = mock_de_xuat
        mock_de_xuat_repo.update_trang_thai.return_value = True
        
        use_case = DuyetDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-001")
        
        # Assert
        assert result.success is True
        mock_de_xuat_repo.update_trang_thai.assert_called_once()
    
    def test_duyet_truong_khoa_not_found(self, mock_tk_repo, mock_de_xuat_repo):
        """Test approval when truong khoa not found"""
        # Arrange
        mock_tk_repo.find_by_user_id.return_value = None
        
        use_case = DuyetDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-invalid", "dx-001")
        
        # Assert
        assert result.success is False
        assert result.error_code == "TRUONG_KHOA_NOT_FOUND"
    
    def test_duyet_de_xuat_not_found(self, mock_tk_repo, mock_de_xuat_repo, mock_truong_khoa):
        """Test approval when de xuat not found"""
        # Arrange
        mock_tk_repo.find_by_user_id.return_value = mock_truong_khoa
        mock_de_xuat_repo.find_by_id.return_value = None
        
        use_case = DuyetDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-invalid")
        
        # Assert
        assert result.success is False
        assert result.error_code == "DE_XUAT_NOT_FOUND"
    
    def test_duyet_forbidden_different_khoa(self, mock_tk_repo, mock_de_xuat_repo, mock_truong_khoa, mock_de_xuat):
        """Test approval forbidden when de xuat belongs to different khoa"""
        # Arrange
        mock_de_xuat["khoa_id"] = "khoa-002"  # Different khoa
        mock_tk_repo.find_by_user_id.return_value = mock_truong_khoa
        mock_de_xuat_repo.find_by_id.return_value = mock_de_xuat
        
        use_case = DuyetDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-001")
        
        # Assert
        assert result.success is False
        assert result.error_code == "FORBIDDEN"


# ==================== TuChoiDeXuatHocPhanByTKUseCase Tests ====================

class TestTuChoiDeXuatHocPhanByTKUseCase:
    """Tests for TuChoiDeXuatHocPhanByTKUseCase"""
    
    def test_tu_choi_success(self, mock_tk_repo, mock_de_xuat_repo, mock_truong_khoa, mock_de_xuat):
        """Test successful rejection by TK"""
        # Arrange
        mock_tk_repo.find_by_user_id.return_value = mock_truong_khoa
        mock_de_xuat_repo.find_by_id.return_value = mock_de_xuat
        mock_de_xuat_repo.update_trang_thai.return_value = True
        
        use_case = TuChoiDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-001", "Không phù hợp chương trình")
        
        # Assert
        assert result.success is True
    
    def test_tu_choi_missing_reason(self, mock_tk_repo, mock_de_xuat_repo):
        """Test rejection with missing reason"""
        # Arrange
        use_case = TuChoiDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-001", "")
        
        # Assert
        assert result.success is False
        assert result.error_code == "MISSING_REASON"
    
    def test_tu_choi_empty_whitespace_reason(self, mock_tk_repo, mock_de_xuat_repo):
        """Test rejection with empty whitespace reason"""
        # Arrange
        use_case = TuChoiDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-001", "   ")
        
        # Assert
        assert result.success is False
        assert result.error_code == "MISSING_REASON"
    
    def test_tu_choi_truong_khoa_not_found(self, mock_tk_repo, mock_de_xuat_repo):
        """Test rejection when truong khoa not found"""
        # Arrange
        mock_tk_repo.find_by_user_id.return_value = None
        
        use_case = TuChoiDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-invalid", "dx-001", "Lý do từ chối")
        
        # Assert
        assert result.success is False
        assert result.error_code == "TRUONG_KHOA_NOT_FOUND"
    
    def test_tu_choi_de_xuat_not_found(self, mock_tk_repo, mock_de_xuat_repo, mock_truong_khoa):
        """Test rejection when de xuat not found"""
        # Arrange
        mock_tk_repo.find_by_user_id.return_value = mock_truong_khoa
        mock_de_xuat_repo.find_by_id.return_value = None
        
        use_case = TuChoiDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-invalid", "Lý do từ chối")
        
        # Assert
        assert result.success is False
        assert result.error_code == "DE_XUAT_NOT_FOUND"
    
    def test_tu_choi_forbidden_different_khoa(self, mock_tk_repo, mock_de_xuat_repo, mock_truong_khoa, mock_de_xuat):
        """Test rejection forbidden when de xuat belongs to different khoa"""
        # Arrange
        mock_de_xuat["khoa_id"] = "khoa-999"  # Different khoa
        mock_tk_repo.find_by_user_id.return_value = mock_truong_khoa
        mock_de_xuat_repo.find_by_id.return_value = mock_de_xuat
        
        use_case = TuChoiDeXuatHocPhanByTKUseCase(mock_tk_repo, mock_de_xuat_repo)
        
        # Act
        result = use_case.execute("user-001", "dx-001", "Lý do từ chối")
        
        # Assert
        assert result.success is False
        assert result.error_code == "FORBIDDEN"
