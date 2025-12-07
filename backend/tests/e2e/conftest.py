"""
E2E Test Shared Fixtures
Provides comprehensive fixtures for all user types and common test data
"""
import pytest
import uuid
from datetime import datetime, timedelta
from django.utils import timezone


class AuthenticatedUser:
    """Wrapper for Users model to satisfy DRF authentication"""
    def __init__(self, user, loai_tai_khoan='sinh_vien'):
        self._user = user
        self.id = user.id
        self.ho_ten = user.ho_ten
        self.email = user.email
        self.tai_khoan = user.tai_khoan
        self.ma_nhan_vien = user.ma_nhan_vien
        self._loai_tai_khoan = loai_tai_khoan
        
    @property
    def is_authenticated(self):
        return True
    
    @property 
    def is_anonymous(self):
        return False
    
    @property
    def loai_tai_khoan(self):
        return self._loai_tai_khoan
    
    def __getattr__(self, name):
        return getattr(self._user, name)


@pytest.fixture
def api_client():
    """API client for making requests"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def setup_base_data():
    """Setup basic data: Khoa, Nganh, HocKy, NienKhoa"""
    from infrastructure.persistence.models import (
        Khoa, NganhHoc, HocKy, NienKhoa
    )
    
    khoa = Khoa.objects.using('neon').create(
        id=uuid.uuid4(),
        ma_khoa="CNTT_TEST",
        ten_khoa="Công nghệ Thông tin Test"
    )
    
    nganh = NganhHoc.objects.using('neon').create(
        id=uuid.uuid4(),
        ma_nganh="KTPM_TEST",
        ten_nganh="Kỹ thuật Phần mềm Test",
        khoa=khoa
    )
    
    nien_khoa = NienKhoa.objects.using('neon').create(
        id=uuid.uuid4(),
        ten_nien_khoa="2024-2025_TEST"
    )
    
    hoc_ky = HocKy.objects.using('neon').create(
        id=uuid.uuid4(),
        ten_hoc_ky="Học kỳ Test",
        ma_hoc_ky="HK_TEST",
        id_nien_khoa=nien_khoa,
        trang_thai_hien_tai=True
    )
    
    return {
        'khoa': khoa,
        'nganh': nganh,
        'nien_khoa': nien_khoa,
        'hoc_ky': hoc_ky
    }


@pytest.fixture
def create_pdt_user(setup_base_data):
    """Create PDT (Phong Dao Tao) user"""
    def _create():
        from infrastructure.persistence.models import (
            Users, TaiKhoan, PhongDaoTao
        )
        from core.utils.password import PasswordService
        
        unique_id = uuid.uuid4().hex[:8]
        
        tai_khoan = TaiKhoan.objects.using('neon').create(
            id=uuid.uuid4(),
            ten_dang_nhap=f"pdt_test_{unique_id}",
            mat_khau=PasswordService.hash_password("test123"),
            loai_tai_khoan="pdt",
            trang_thai_hoat_dong=True
        )
        
        user = Users.objects.using('neon').create(
            id=uuid.uuid4(),
            ho_ten=f"PDT User {unique_id}",
            email=f"pdt_{unique_id}@test.com",
            tai_khoan=tai_khoan
        )
        
        pdt = PhongDaoTao.objects.using('neon').create(
            id=user,
            chuc_vu="Nhân viên"
        )
        
        return AuthenticatedUser(user, 'pdt')
    
    return _create


@pytest.fixture
def create_tk_user(setup_base_data):
    """Create TK (Truong Khoa) user"""
    def _create():
        from infrastructure.persistence.models import (
            Users, TaiKhoan, TruongKhoa
        )
        from core.utils.password import PasswordService
        
        unique_id = uuid.uuid4().hex[:8]
        khoa = setup_base_data['khoa']
        
        tai_khoan = TaiKhoan.objects.using('neon').create(
            id=uuid.uuid4(),
            ten_dang_nhap=f"tk_test_{unique_id}",
            mat_khau=PasswordService.hash_password("test123"),
            loai_tai_khoan="truong_khoa",
            trang_thai_hoat_dong=True
        )
        
        user = Users.objects.using('neon').create(
            id=uuid.uuid4(),
            ho_ten=f"TK User {unique_id}",
            email=f"tk_{unique_id}@test.com",
            tai_khoan=tai_khoan
        )
        
        tk = TruongKhoa.objects.using('neon').create(
            id=user,
            khoa=khoa
        )
        
        return AuthenticatedUser(user, 'truong_khoa')
    
    return _create


@pytest.fixture
def create_tlk_user(setup_base_data):
    """Create TLK (Tro Ly Khoa) user"""
    def _create():
        from infrastructure.persistence.models import (
            Users, TaiKhoan, TroLyKhoa
        )
        from core.utils.password import PasswordService
        
        unique_id = uuid.uuid4().hex[:8]
        khoa = setup_base_data['khoa']
        
        tai_khoan = TaiKhoan.objects.using('neon').create(
            id=uuid.uuid4(),
            ten_dang_nhap=f"tlk_test_{unique_id}",
            mat_khau=PasswordService.hash_password("test123"),
            loai_tai_khoan="tro_ly_khoa",
            trang_thai_hoat_dong=True
        )
        
        user = Users.objects.using('neon').create(
            id=uuid.uuid4(),
            ho_ten=f"TLK User {unique_id}",
            email=f"tlk_{unique_id}@test.com",
            tai_khoan=tai_khoan
        )
        
        tlk = TroLyKhoa.objects.using('neon').create(
            id=user,
            khoa=khoa
        )
        
        return AuthenticatedUser(user, 'tro_ly_khoa')
    
    return _create


@pytest.fixture
def create_gv_user(setup_base_data):
    """Create GV (Giang Vien) user"""
    def _create():
        from infrastructure.persistence.models import (
            Users, TaiKhoan, GiangVien
        )
        from core.utils.password import PasswordService
        
        unique_id = uuid.uuid4().hex[:8]
        khoa = setup_base_data['khoa']
        
        tai_khoan = TaiKhoan.objects.using('neon').create(
            id=uuid.uuid4(),
            ten_dang_nhap=f"gv_test_{unique_id}",
            mat_khau=PasswordService.hash_password("test123"),
            loai_tai_khoan="giang_vien",
            trang_thai_hoat_dong=True
        )
        
        user = Users.objects.using('neon').create(
            id=uuid.uuid4(),
            ho_ten=f"GV User {unique_id}",
            email=f"gv_{unique_id}@test.com",
            tai_khoan=tai_khoan
        )
        
        gv = GiangVien.objects.using('neon').create(
            id=user,
            khoa=khoa,
            chuyen_mon="Computer Science",
            trinh_do="Thạc sĩ"
        )
        
        return AuthenticatedUser(user, 'giang_vien')
    
    return _create


@pytest.fixture
def create_sv_user(setup_base_data):
    """Create SV (Sinh Vien) user"""
    def _create():
        from infrastructure.persistence.models import (
            Users, TaiKhoan, SinhVien
        )
        from core.utils.password import PasswordService
        
        unique_id = uuid.uuid4().hex[:8]
        khoa = setup_base_data['khoa']
        nganh = setup_base_data['nganh']
        
        tai_khoan = TaiKhoan.objects.using('neon').create(
            id=uuid.uuid4(),
            ten_dang_nhap=f"sv_test_{unique_id}",
            mat_khau=PasswordService.hash_password("test123"),
            loai_tai_khoan="sinh_vien",
            trang_thai_hoat_dong=True
        )
        
        user = Users.objects.using('neon').create(
            id=uuid.uuid4(),
            ho_ten=f"SV User {unique_id}",
            email=f"sv_{unique_id}@test.com",
            tai_khoan=tai_khoan
        )
        
        sv = SinhVien.objects.using('neon').create(
            id=user,
            ma_so_sinh_vien=f"SV{unique_id}",
            khoa=khoa,
            nganh=nganh,
            lop="KTPM2024"
        )
        
        return AuthenticatedUser(user, 'sinh_vien')
    
    return _create


@pytest.fixture
def create_mon_hoc(setup_base_data):
    """Create MonHoc test data"""
    def _create(ma_mon=None, ten_mon=None, so_tin_chi=3):
        from infrastructure.persistence.models import MonHoc
        
        unique_id = uuid.uuid4().hex[:6]
        khoa = setup_base_data['khoa']
        
        mon_hoc = MonHoc.objects.using('neon').create(
            id=uuid.uuid4(),
            ma_mon=ma_mon or f"MH_{unique_id}",
            ten_mon=ten_mon or f"Môn học Test {unique_id}",
            so_tin_chi=so_tin_chi,
            khoa=khoa
        )
        
        return mon_hoc
    
    return _create


@pytest.fixture
def create_hoc_phan(setup_base_data, create_mon_hoc):
    """Create HocPhan test data"""
    def _create(mon_hoc=None):
        from infrastructure.persistence.models import HocPhan
        
        if mon_hoc is None:
            mon_hoc = create_mon_hoc()
        
        hoc_ky = setup_base_data['hoc_ky']
        
        hoc_phan = HocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            mon_hoc=mon_hoc,
            ten_hoc_phan=mon_hoc.ten_mon,
            id_hoc_ky=hoc_ky,
            trang_thai_mo=True
        )
        
        return hoc_phan
    
    return _create


@pytest.fixture
def create_lop_hoc_phan(setup_base_data, create_hoc_phan, create_gv_user):
    """Create LopHocPhan test data"""
    def _create(hoc_phan=None, giang_vien=None):
        from infrastructure.persistence.models import LopHocPhan
        
        if hoc_phan is None:
            hoc_phan = create_hoc_phan()
        
        unique_id = uuid.uuid4().hex[:6]
        
        lop = LopHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_phan=hoc_phan,
            ma_lop=f"LHP_{unique_id}",
            giang_vien_id=giang_vien.id if giang_vien else None,
            so_luong_toi_da=50,
            so_luong_hien_tai=0,
            trang_thai_lop='dang_mo',
            ngay_bat_dau=timezone.now().date(),
            ngay_ket_thuc=(timezone.now() + timedelta(days=90)).date()
        )
        
        return lop
    
    return _create


@pytest.fixture
def create_ky_phase(setup_base_data):
    """Create KyPhase test data"""
    def _create(phase='dang_ky_hoc_phan', is_enabled=True):
        from infrastructure.persistence.models import KyPhase
        
        hoc_ky = setup_base_data['hoc_ky']
        now = timezone.now()
        
        ky_phase = KyPhase.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_ky=hoc_ky,
            phase=phase,
            start_at=now - timedelta(days=1),
            end_at=now + timedelta(days=30),
            is_enabled=is_enabled
        )
        
        return ky_phase
    
    return _create


@pytest.fixture
def create_phong(setup_base_data):
    """Create Phong (Room) test data"""
    def _create(ma_phong=None, suc_chua=50):
        from infrastructure.persistence.models import Phong, CoSo
        
        unique_id = uuid.uuid4().hex[:6]
        khoa = setup_base_data['khoa']
        
        # Create CoSo if not exists
        co_so, _ = CoSo.objects.using('neon').get_or_create(
            ten_co_so="Cơ sở Test",
            defaults={'id': uuid.uuid4(), 'dia_chi': 'Test Address'}
        )
        
        phong = Phong.objects.using('neon').create(
            id=uuid.uuid4(),
            ma_phong=ma_phong or f"P_{unique_id}",
            co_so=co_so,
            suc_chua=suc_chua,
            da_dc_su_dung=False,
            khoa=khoa
        )
        
        return phong
    
    return _create


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup test data after each test"""
    yield
    # Cleanup is handled by transaction rollback in Django tests
