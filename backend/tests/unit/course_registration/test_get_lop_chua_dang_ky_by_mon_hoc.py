import pytest
from unittest.mock import Mock, MagicMock
from application.course_registration.use_cases.get_lop_chua_dang_ky_by_mon_hoc_use_case import GetLopChuaDangKyByMonHocUseCase
from core.types import ServiceResult

class TestGetLopChuaDangKyByMonHocUseCase:
    @pytest.fixture
    def mock_lop_hoc_phan_repo(self):
        return Mock()

    @pytest.fixture
    def mock_dang_ky_hp_repo(self):
        return Mock()

    @pytest.fixture
    def use_case(self, mock_lop_hoc_phan_repo, mock_dang_ky_hp_repo):
        return GetLopChuaDangKyByMonHocUseCase(mock_lop_hoc_phan_repo, mock_dang_ky_hp_repo)

    def test_execute_success(self, use_case, mock_lop_hoc_phan_repo, mock_dang_ky_hp_repo):
        # Arrange
        sinh_vien_id = "sv1"
        mon_hoc_id = "mh1"
        hoc_ky_id = "hk1"
        
        # Mock registered classes for this student in this semester
        # Suppose student is registered for class 'lhp1' of subject 'mh1' (which is what we want to switch FROM)
        # But wait, the requirement is "Get list of classes ... excluding classes the student is already registered for"
        # So if I am registered for LHP_A of Subject X, and I want to switch, I need to see LHP_B, LHP_C of Subject X.
        
        mock_dang_ky = MagicMock()
        mock_dang_ky.lop_hoc_phan.id = "lhp1"
        mock_dang_ky_hp_repo.get_registered_classes_by_subject.return_value = [mock_dang_ky]
        
        # Mock all classes for subject in semester
        lhp1 = MagicMock()
        lhp1.id = "lhp1"
        lhp1.ma_lop = "LHP001"
        lhp1.so_luong_hien_tai = 10
        lhp1.so_luong_toi_da = 50
        
        lhp2 = MagicMock()
        lhp2.id = "lhp2"
        lhp2.ma_lop = "LHP002"
        lhp2.so_luong_hien_tai = 5
        lhp2.so_luong_toi_da = 50
        
        lhp3 = MagicMock()
        lhp3.id = "lhp3"
        lhp3.ma_lop = "LHP003"
        lhp3.so_luong_hien_tai = 50 # Full
        lhp3.so_luong_toi_da = 50
        
        mock_lop_hoc_phan_repo.get_by_mon_hoc_and_hoc_ky.return_value = [lhp1, lhp2, lhp3]

        # Act
        result = use_case.execute(sinh_vien_id, mon_hoc_id, hoc_ky_id)

        # Assert
        assert result.success
        data = result.data
        assert len(data) == 2 # Should exclude lhp1 (registered), include lhp2, lhp3 (even if full, usually we show them but disable)
        # Wait, usually "Get list of classes to switch" might imply showing available ones. 
        # But let's assume we show all EXCEPT the one we are in.
        
        ids = [item['id'] for item in data]
        assert "lhp1" not in ids
        assert "lhp2" in ids
        assert "lhp3" in ids

    def test_execute_missing_params(self, use_case):
        result = use_case.execute("sv1", "", "hk1")
        assert not result.success
        assert result.error_code == "MISSING_PARAMS"

    def test_execute_no_classes_found(self, use_case, mock_lop_hoc_phan_repo, mock_dang_ky_hp_repo):
        mock_dang_ky_hp_repo.get_registered_classes_by_subject.return_value = []
        mock_lop_hoc_phan_repo.get_by_mon_hoc_and_hoc_ky.return_value = []
        
        result = use_case.execute("sv1", "mh1", "hk1")
        assert result.success
        assert result.data == []
