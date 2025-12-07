"""
Unit Tests for TLK (Trợ Lý Khoa) Use Cases
Tests: CreateDeXuatHocPhan, GetDeXuatHocPhan, GetGiangVienByKhoa, GetMonHocByKhoa, 
       GetPhongHocByTLK, XepThoiKhoaBieu
"""
import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    django.setup()


class TestCreateDeXuatHocPhanUseCase:
    """Tests for CreateDeXuatHocPhanUseCase"""
    
    @pytest.fixture
    def mock_tlk_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_de_xuat_repo(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_tlk_repo, mock_de_xuat_repo):
        from application.tlk.use_cases.create_de_xuat_hoc_phan_use_case import CreateDeXuatHocPhanUseCase
        return CreateDeXuatHocPhanUseCase(
            tlk_repo=mock_tlk_repo, 
            de_xuat_repo=mock_de_xuat_repo
        )
    
    def test_execute_success(self, use_case, mock_tlk_repo, mock_de_xuat_repo):
        """
        Given: Valid proposal data
        When: CreateDeXuatHocPhanUseCase.execute() is called
        Then: Return success with created proposal
        """
        from application.tlk.use_cases.create_de_xuat_hoc_phan_use_case import CreateDeXuatHocPhanRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        mock_de_xuat_repo.create_de_xuat.return_value = True
        
        request = CreateDeXuatHocPhanRequest(
            ma_hoc_phan="mh-001",
            ma_giang_vien="gv-001"
        )
        
        result = use_case.execute(
            user_id="tlk-001",
            request=request,
            hoc_ky_id="hk-001"
        )
        
        assert result.success is True
        mock_de_xuat_repo.create_de_xuat.assert_called_once()
    
    def test_execute_fail_tlk_not_found(self, use_case, mock_tlk_repo, mock_de_xuat_repo):
        """
        Given: TLK user not found
        When: CreateDeXuatHocPhanUseCase.execute() is called
        Then: Return fail with error message
        """
        from application.tlk.use_cases.create_de_xuat_hoc_phan_use_case import CreateDeXuatHocPhanRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = None
        
        request = CreateDeXuatHocPhanRequest(
            ma_hoc_phan="mh-001",
            ma_giang_vien="gv-001"
        )
        
        result = use_case.execute(
            user_id="tlk-invalid",
            request=request,
            hoc_ky_id="hk-001"
        )
        
        assert result.success is False
        assert "không tìm thấy" in result.message.lower()
    
    def test_execute_fail_create_de_xuat_fails(self, use_case, mock_tlk_repo, mock_de_xuat_repo):
        """
        Given: Valid TLK but de xuat creation fails
        When: CreateDeXuatHocPhanUseCase.execute() is called
        Then: Return fail
        """
        from application.tlk.use_cases.create_de_xuat_hoc_phan_use_case import CreateDeXuatHocPhanRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        mock_de_xuat_repo.create_de_xuat.return_value = False
        
        request = CreateDeXuatHocPhanRequest(
            ma_hoc_phan="mh-001",
            ma_giang_vien=""
        )
        
        result = use_case.execute(
            user_id="tlk-001",
            request=request,
            hoc_ky_id="hk-001"
        )
        
        assert result.success is False


class TestGetDeXuatHocPhanUseCase:
    """Tests for GetDeXuatHocPhanUseCase"""
    
    @pytest.fixture
    def mock_tlk_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_de_xuat_repo(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_tlk_repo, mock_de_xuat_repo):
        from application.tlk.use_cases.get_de_xuat_hoc_phan_use_case import GetDeXuatHocPhanUseCase
        return GetDeXuatHocPhanUseCase(
            tlk_repo=mock_tlk_repo, 
            de_xuat_repo=mock_de_xuat_repo
        )
    
    def test_execute_success(self, use_case, mock_tlk_repo, mock_de_xuat_repo):
        """
        Given: TLK has proposals
        When: GetDeXuatHocPhanUseCase.execute() is called
        Then: Return list of proposals
        """
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        
        # Mock de xuat DTOs
        mock_dx1 = Mock()
        mock_dx1.id = "dx-001"
        mock_dx1.ma_hoc_phan = "CS101"
        mock_dx1.ten_hoc_phan = "Lập trình"
        mock_dx1.so_tin_chi = 3
        mock_dx1.giang_vien = "Nguyễn Văn A"
        mock_dx1.trang_thai = "cho_duyet"
        
        mock_dx2 = Mock()
        mock_dx2.id = "dx-002"
        mock_dx2.ma_hoc_phan = "CS102"
        mock_dx2.ten_hoc_phan = "CTDL"
        mock_dx2.so_tin_chi = 4
        mock_dx2.giang_vien = "Trần Văn B"
        mock_dx2.trang_thai = "da_duyet"
        
        mock_de_xuat_repo.get_de_xuat_by_khoa.return_value = [mock_dx1, mock_dx2]
        
        result = use_case.execute("tlk-001", "hk-001")
        
        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["maHocPhan"] == "CS101"
        assert result.data[1]["trangThai"] == "da_duyet"
    
    def test_execute_tlk_not_found(self, use_case, mock_tlk_repo, mock_de_xuat_repo):
        """
        Given: TLK not found
        When: GetDeXuatHocPhanUseCase.execute() is called
        Then: Return not found
        """
        mock_tlk_repo.get_khoa_id_by_user.return_value = None
        
        result = use_case.execute("tlk-invalid", "hk-001")
        
        assert result.success is False
        assert "không tìm thấy" in result.message.lower()
    
    def test_execute_empty_list(self, use_case, mock_tlk_repo, mock_de_xuat_repo):
        """
        Given: No proposals for khoa
        When: GetDeXuatHocPhanUseCase.execute() is called
        Then: Return empty list
        """
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        mock_de_xuat_repo.get_de_xuat_by_khoa.return_value = []
        
        result = use_case.execute("tlk-001", "hk-001")
        
        assert result.success is True
        assert result.data == []


class TestGetGiangVienByKhoaUseCase:
    """Tests for GetGiangVienByKhoaUseCase"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_repository):
        from application.tlk.use_cases.get_giang_vien_use_case import GetGiangVienByKhoaUseCase
        return GetGiangVienByKhoaUseCase(repository=mock_repository)
    
    def test_execute_success(self, use_case, mock_repository):
        """
        Given: Khoa has lecturers
        When: GetGiangVienByKhoaUseCase.execute() is called
        Then: Return list of lecturers
        """
        mock_repository.get_khoa_id_by_user.return_value = "khoa-001"
        
        # Mock GiangVien DTOs
        mock_gv1 = Mock()
        mock_gv1.id = "gv-001"
        mock_gv1.ho_ten = "Nguyen Van A"
        
        mock_gv2 = Mock()
        mock_gv2.id = "gv-002"
        mock_gv2.ho_ten = "Tran Van B"
        
        mock_repository.get_giang_vien_by_khoa.return_value = [mock_gv1, mock_gv2]
        
        result = use_case.execute("tlk-001")
        
        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["ho_ten"] == "Nguyen Van A"
    
    def test_execute_khoa_not_found(self, use_case, mock_repository):
        """
        Given: TLK's khoa not found
        When: GetGiangVienByKhoaUseCase.execute() is called
        Then: Return fail
        """
        mock_repository.get_khoa_id_by_user.return_value = None
        
        result = use_case.execute("tlk-invalid")
        
        assert result.success is False


class TestGetMonHocByKhoaUseCase:
    """Tests for GetMonHocByKhoaUseCase"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_repository):
        from application.tlk.use_cases.get_mon_hoc_use_case import GetMonHocByKhoaUseCase
        return GetMonHocByKhoaUseCase(repository=mock_repository)
    
    def test_execute_success(self, use_case, mock_repository):
        """
        Given: Khoa has subjects
        When: GetMonHocByKhoaUseCase.execute() is called
        Then: Return list of subjects
        """
        mock_repository.get_khoa_id_by_user.return_value = "khoa-001"
        
        # Mock MonHoc DTOs
        mock_mh1 = Mock()
        mock_mh1.id = "mh-001"
        mock_mh1.ma_mon = "CS101"
        mock_mh1.ten_mon = "Lập trình"
        mock_mh1.so_tin_chi = 3
        
        mock_mh2 = Mock()
        mock_mh2.id = "mh-002"
        mock_mh2.ma_mon = "CS102"
        mock_mh2.ten_mon = "CTDL"
        mock_mh2.so_tin_chi = 4
        
        mock_repository.get_mon_hoc_by_khoa.return_value = [mock_mh1, mock_mh2]
        
        result = use_case.execute("tlk-001")
        
        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["ma_mon"] == "CS101"
    
    def test_execute_khoa_not_found(self, use_case, mock_repository):
        """
        Given: TLK's khoa not found
        When: GetMonHocByKhoaUseCase.execute() is called
        Then: Return fail
        """
        mock_repository.get_khoa_id_by_user.return_value = None
        
        result = use_case.execute("tlk-invalid")
        
        assert result.success is False


class TestGetPhongHocByTLKUseCase:
    """Tests for GetPhongHocByTLKUseCase"""
    
    @pytest.fixture
    def mock_tlk_repository(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_tlk_repository):
        from application.tlk.use_cases.get_phong_hoc_use_cases import GetPhongHocByTLKUseCase
        return GetPhongHocByTLKUseCase(tlk_repository=mock_tlk_repository)
    
    def test_execute_success(self, use_case, mock_tlk_repository):
        """
        Given: System has rooms for khoa
        When: GetPhongHocByTLKUseCase.execute() is called
        Then: Return list of rooms
        """
        mock_tlk_repository.get_khoa_id_by_user.return_value = "khoa-001"
        
        # Mock PhongHoc DTOs
        mock_ph1 = Mock()
        mock_ph1.id = "ph-001"
        mock_ph1.ma_phong = "A101"
        mock_ph1.ten_phong = "Phòng A101"
        mock_ph1.suc_chua = 50
        
        mock_ph2 = Mock()
        mock_ph2.id = "ph-002"
        mock_ph2.ma_phong = "A102"
        mock_ph2.ten_phong = "Phòng A102"
        mock_ph2.suc_chua = 40
        
        mock_tlk_repository.get_phong_hoc_by_khoa.return_value = [mock_ph1, mock_ph2]
        
        result = use_case.execute("tlk-001")
        
        assert result.success is True
        assert isinstance(result.data, list)
        assert len(result.data) == 2
    
    def test_execute_khoa_not_found(self, use_case, mock_tlk_repository):
        """
        Given: TLK's khoa not found
        When: GetPhongHocByTLKUseCase.execute() is called
        Then: Return fail
        """
        mock_tlk_repository.get_khoa_id_by_user.return_value = None
        
        result = use_case.execute("tlk-invalid")
        
        assert result.success is False


class TestXepThoiKhoaBieuUseCase:
    """Tests for XepThoiKhoaBieuUseCase"""
    
    @pytest.fixture
    def mock_tlk_repo(self):
        return Mock()
    
    @pytest.fixture
    def mock_tkb_repo(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_tlk_repo, mock_tkb_repo):
        from application.tlk.use_cases.xep_thoi_khoa_bieu_use_case import XepThoiKhoaBieuUseCase
        return XepThoiKhoaBieuUseCase(
            tlk_repo=mock_tlk_repo,
            tkb_repo=mock_tkb_repo
        )
    
    def test_execute_success(self, use_case, mock_tlk_repo, mock_tkb_repo):
        """
        Given: Valid TKB data
        When: XepThoiKhoaBieuUseCase.execute() is called
        Then: Return success
        """
        from application.tlk.use_cases.xep_thoi_khoa_bieu_use_case import XepTKBRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        mock_tkb_repo.xep_thoi_khoa_bieu.return_value = {
            "success": True, 
            "message": "Thành công",
            "created_count": 1
        }
        
        request = XepTKBRequest(
            ma_hoc_phan="mh-001",
            hoc_ky_id="hk-001",
            danh_sach_lop=[
                {
                    "id": None,
                    "tenLop": "Lớp 1",
                    "phongHocId": "ph-001",
                    "ngayBatDau": "2024-01-15",
                    "ngayKetThuc": "2024-05-15",
                    "tietBatDau": 1,
                    "tietKetThuc": 3,
                    "thuTrongTuan": 2
                }
            ]
        )
        
        result = use_case.execute(
            user_id="tlk-001",
            request=request,
            giang_vien_id="gv-001"
        )
        
        assert result.success is True
    
    def test_execute_fail_tlk_not_found(self, use_case, mock_tlk_repo, mock_tkb_repo):
        """
        Given: TLK not found
        When: XepThoiKhoaBieuUseCase.execute() is called
        Then: Return fail
        """
        from application.tlk.use_cases.xep_thoi_khoa_bieu_use_case import XepTKBRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = None
        
        request = XepTKBRequest(
            ma_hoc_phan="mh-001",
            hoc_ky_id="hk-001",
            danh_sach_lop=[{"tenLop": "Lớp 1"}]
        )
        
        result = use_case.execute(
            user_id="tlk-invalid",
            request=request
        )
        
        assert result.success is False
    
    def test_execute_fail_empty_ma_hoc_phan(self, use_case, mock_tlk_repo, mock_tkb_repo):
        """
        Given: Empty ma_hoc_phan
        When: XepThoiKhoaBieuUseCase.execute() is called
        Then: Return fail
        """
        from application.tlk.use_cases.xep_thoi_khoa_bieu_use_case import XepTKBRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        
        request = XepTKBRequest(
            ma_hoc_phan="",
            hoc_ky_id="hk-001",
            danh_sach_lop=[{"tenLop": "Lớp 1"}]
        )
        
        result = use_case.execute(
            user_id="tlk-001",
            request=request
        )
        
        assert result.success is False
    
    def test_execute_fail_empty_hoc_ky(self, use_case, mock_tlk_repo, mock_tkb_repo):
        """
        Given: Empty hoc_ky_id
        When: XepThoiKhoaBieuUseCase.execute() is called
        Then: Return fail
        """
        from application.tlk.use_cases.xep_thoi_khoa_bieu_use_case import XepTKBRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        
        request = XepTKBRequest(
            ma_hoc_phan="mh-001",
            hoc_ky_id="",
            danh_sach_lop=[{"tenLop": "Lớp 1"}]
        )
        
        result = use_case.execute(
            user_id="tlk-001",
            request=request
        )
        
        assert result.success is False
    
    def test_execute_fail_empty_danh_sach_lop(self, use_case, mock_tlk_repo, mock_tkb_repo):
        """
        Given: Empty danh_sach_lop
        When: XepThoiKhoaBieuUseCase.execute() is called
        Then: Return fail
        """
        from application.tlk.use_cases.xep_thoi_khoa_bieu_use_case import XepTKBRequest
        
        mock_tlk_repo.get_khoa_id_by_user.return_value = "khoa-001"
        
        request = XepTKBRequest(
            ma_hoc_phan="mh-001",
            hoc_ky_id="hk-001",
            danh_sach_lop=[]
        )
        
        result = use_case.execute(
            user_id="tlk-001",
            request=request
        )
        
        assert result.success is False
