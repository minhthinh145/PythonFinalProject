"""
TDD Tests - Get De Xuat Hoc Phan for Truong Khoa

API: GET /api/tk/de-xuat-hoc-phan
FE expects:
{
    "isSuccess": true,
    "data": [
        {
            "id": "uuid",
            "maHocPhan": "COMP1060",
            "tenHocPhan": "Phân tích thiết kế hướng đối tượng",
            "soTinChi": 3,
            "giangVien": "Nguyễn Văn A",
            "trangThai": "cho_duyet"
        }
    ]
}
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4


class TestGetDeXuatHocPhanForTKUseCase:
    """Test cases for GetDeXuatHocPhanForTKUseCase"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tk_repo = Mock()
        self.de_xuat_repo = Mock()
        
        # Import after mocking
        from application.tk.use_cases.get_de_xuat_hoc_phan_use_case import GetDeXuatHocPhanForTKUseCase
        self.use_case = GetDeXuatHocPhanForTKUseCase(
            tk_repo=self.tk_repo,
            de_xuat_repo=self.de_xuat_repo
        )
        
        # Mock truong khoa
        self.user_id = str(uuid4())
        self.khoa_id = str(uuid4())
        self.hoc_ky_id = str(uuid4())
    
    def test_get_de_xuat_success(self):
        """Should return list of de xuat for truong khoa's khoa with trang_thai = cho_duyet"""
        # Arrange - Repository returns dict
        self.tk_repo.find_by_user_id.return_value = {
            'id': self.user_id,
            'khoa_id': self.khoa_id,
        }
        
        # Mock de xuat list - Repository returns DeXuatHocPhanForTKDTO
        from application.tk.interfaces import DeXuatHocPhanForTKDTO
        mock_de_xuat = DeXuatHocPhanForTKDTO(
            id=str(uuid4()),
            ma_hoc_phan="COMP1060",
            ten_hoc_phan="Phân tích thiết kế hướng đối tượng",
            so_tin_chi=3,
            giang_vien="Nguyễn Văn A",
            trang_thai="cho_duyet",
        )
        
        self.de_xuat_repo.find_by_khoa_and_status.return_value = [mock_de_xuat]
        
        # Act
        result = self.use_case.execute(self.user_id)
        
        # Assert
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["maHocPhan"] == "COMP1060"
        assert result.data[0]["tenHocPhan"] == "Phân tích thiết kế hướng đối tượng"
        assert result.data[0]["soTinChi"] == 3
        assert result.data[0]["giangVien"] == "Nguyễn Văn A"
        assert result.data[0]["trangThai"] == "cho_duyet"
    
    def test_truong_khoa_not_found(self):
        """Should fail if truong khoa not found"""
        # Arrange
        self.tk_repo.find_by_user_id.return_value = None
        
        # Act
        result = self.use_case.execute(self.user_id, self.hoc_ky_id)
        
        # Assert
        assert result.success is False
        assert "Không tìm thấy trưởng khoa" in result.message
    
    def test_empty_list_when_no_proposals(self):
        """Should return empty list when no proposals exist"""
        # Arrange - Repository returns dict
        self.tk_repo.find_by_user_id.return_value = {
            'id': self.user_id,
            'khoa_id': self.khoa_id,
        }
        self.de_xuat_repo.find_by_khoa_and_status.return_value = []
        
        # Act
        result = self.use_case.execute(self.user_id)
        
        # Assert
        assert result.success is True
        assert result.data == []


class TestDuyetDeXuatHocPhanUseCase:
    """Test cases for DuyetDeXuatHocPhanByTKUseCase"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tk_repo = Mock()
        self.de_xuat_repo = Mock()
        
        from application.tk.use_cases.duyet_de_xuat_use_case import DuyetDeXuatHocPhanByTKUseCase
        self.use_case = DuyetDeXuatHocPhanByTKUseCase(
            tk_repo=self.tk_repo,
            de_xuat_repo=self.de_xuat_repo
        )
        
        self.user_id = str(uuid4())
        self.de_xuat_id = str(uuid4())
        self.khoa_id = str(uuid4())
    
    def test_duyet_success(self):
        """Should approve proposal and change status to da_duyet_tk"""
        # Arrange - Repository returns dicts
        self.tk_repo.find_by_user_id.return_value = {
            'id': self.user_id,
            'khoa_id': self.khoa_id,
        }
        
        self.de_xuat_repo.find_by_id.return_value = {
            'id': self.de_xuat_id,
            'khoa_id': self.khoa_id,
            'trang_thai': "cho_duyet",
        }
        self.de_xuat_repo.update_trang_thai.return_value = True
        
        # Act
        result = self.use_case.execute(self.user_id, self.de_xuat_id)
        
        # Assert
        assert result.success is True
        self.de_xuat_repo.update_trang_thai.assert_called_once()
    
    def test_duyet_fail_wrong_khoa(self):
        """Should fail if de xuat belongs to different khoa"""
        # Arrange - Repository returns dicts
        self.tk_repo.find_by_user_id.return_value = {
            'id': self.user_id,
            'khoa_id': self.khoa_id,
        }
        
        different_khoa_id = str(uuid4())
        self.de_xuat_repo.find_by_id.return_value = {
            'id': self.de_xuat_id,
            'khoa_id': different_khoa_id,  # Different khoa
            'trang_thai': "cho_duyet",
        }
        
        # Act
        result = self.use_case.execute(self.user_id, self.de_xuat_id)
        
        # Assert
        assert result.success is False
        assert "không có quyền" in result.message.lower()
    
    def test_duyet_fail_de_xuat_not_found(self):
        """Should fail if de xuat not found"""
        # Arrange - Repository returns dict for tk
        self.tk_repo.find_by_user_id.return_value = {
            'id': self.user_id,
            'khoa_id': self.khoa_id,
        }
        self.de_xuat_repo.find_by_id.return_value = None
        
        # Act
        result = self.use_case.execute(self.user_id, self.de_xuat_id)
        
        # Assert
        assert result.success is False
        assert "Không tìm thấy đề xuất" in result.message


class TestTuChoiDeXuatHocPhanUseCase:
    """Test cases for TuChoiDeXuatHocPhanByTKUseCase"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tk_repo = Mock()
        self.de_xuat_repo = Mock()
        
        from application.tk.use_cases.tu_choi_de_xuat_use_case import TuChoiDeXuatHocPhanByTKUseCase
        self.use_case = TuChoiDeXuatHocPhanByTKUseCase(
            tk_repo=self.tk_repo,
            de_xuat_repo=self.de_xuat_repo
        )
        
        self.user_id = str(uuid4())
        self.de_xuat_id = str(uuid4())
        self.khoa_id = str(uuid4())
    
    def test_tu_choi_success(self):
        """Should reject proposal with reason"""
        # Arrange - Repository returns dicts
        self.tk_repo.find_by_user_id.return_value = {
            'id': self.user_id,
            'khoa_id': self.khoa_id,
        }
        
        self.de_xuat_repo.find_by_id.return_value = {
            'id': self.de_xuat_id,
            'khoa_id': self.khoa_id,
            'trang_thai': "cho_duyet",
        }
        self.de_xuat_repo.reject.return_value = True
        
        # Act
        result = self.use_case.execute(
            self.user_id, 
            self.de_xuat_id, 
            ly_do="Chưa đủ giảng viên"
        )
        
        # Assert
        assert result.success is True
        self.de_xuat_repo.reject.assert_called_once()
    
    def test_tu_choi_fail_missing_reason(self):
        """Should fail if reason is empty"""
        # Arrange - Repository returns dicts
        self.tk_repo.find_by_user_id.return_value = {
            'id': self.user_id,
            'khoa_id': self.khoa_id,
        }
        
        self.de_xuat_repo.find_by_id.return_value = {
            'id': self.de_xuat_id,
            'khoa_id': self.khoa_id,
            'trang_thai': "cho_duyet",
        }
        
        # Act
        result = self.use_case.execute(self.user_id, self.de_xuat_id, ly_do="")
        
        # Assert
        assert result.success is False
        assert "lý do" in result.message.lower()
