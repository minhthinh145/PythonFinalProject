"""
E2E Tests for Enrollment API
"""
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from infrastructure.persistence.models import (
    Users, TaiKhoan, SinhVien, Khoa, NganhHoc, 
    HocKy, NienKhoa, KyPhase, DotDangKy, 
    HocPhan, MonHoc, GhiDanhHocPhan
)
from django.utils import timezone
from datetime import timedelta
import uuid

@pytest.mark.django_db(databases=['default', 'neon'])
class TestEnrollmentAPI:
    
    @pytest.fixture
    def client(self):
        return APIClient()
        
    @pytest.fixture
    def setup_data(self):
        # Create basic data
        khoa = Khoa.objects.create(id=uuid.uuid4(), ma_khoa="CNTT", ten_khoa="Cong nghe thong tin")
        nganh = NganhHoc.objects.create(id=uuid.uuid4(), ma_nganh="KTPM", ten_nganh="Ky thuat phan mem", khoa=khoa)
        
        # Create User & SinhVien
        tk = TaiKhoan.objects.create(
            id=uuid.uuid4(), 
            ten_dang_nhap="sv1", 
            mat_khau="hashed", 
            loai_tai_khoan="sinh_vien",
            trang_thai_hoat_dong=True
        )
        user = Users.objects.create(id=uuid.uuid4(), ho_ten="Sinh Vien 1", email="sv1@test.com", tai_khoan=tk)
        sv = SinhVien.objects.create(
            id=user, 
            ma_so_sinh_vien="SV001", 
            khoa=khoa, 
            nganh=nganh
        )
        
        # Create HocKy & Phase
        nk = NienKhoa.objects.create(id=uuid.uuid4(), ten_nien_khoa="2024-2025")
        hk = HocKy.objects.create(
            id=uuid.uuid4(), 
            ten_hoc_ky="Hoc Ky 1", 
            ma_hoc_ky="HK1", 
            id_nien_khoa=nk,
            trang_thai_hien_tai=True
        )
        
        now = timezone.now()
        KyPhase.objects.create(
            id=uuid.uuid4(),
            hoc_ky=hk,
            phase="ghi_danh",
            start_at=now - timedelta(days=1),
            end_at=now + timedelta(days=1),
            is_enabled=True
        )
        
        DotDangKy.objects.create(
            id=uuid.uuid4(),
            hoc_ky=hk,
            loai_dot="ghi_danh",
            is_check_toan_truong=True,
            thoi_gian_bat_dau=now - timedelta(days=1),
            thoi_gian_ket_thuc=now + timedelta(days=1)
        )
        
        # Create MonHoc & HocPhan
        mh = MonHoc.objects.create(id=uuid.uuid4(), ma_mon="M01", ten_mon="Lap trinh Web", so_tin_chi=3, khoa=khoa)
        hp = HocPhan.objects.create(
            id=uuid.uuid4(),
            mon_hoc=mh,
            ten_hoc_phan="Lop 01",
            id_hoc_ky=hk,
            trang_thai_mo=True
        )
        
        return {
            'user': user,
            'tk': tk,
            'hp': hp
        }

    def test_check_ghi_danh(self, client, setup_data):
        client.force_authenticate(user=setup_data['user'])
        
        response = client.get('/api/sv/check-ghi-danh')
        
        assert response.status_code == 200
        assert response.data['isSuccess'] is True
        assert response.data['message'] == "Đợt ghi danh toàn trường đang mở, sinh viên có thể ghi danh"

    def test_get_mon_hoc_ghi_danh(self, client, setup_data):
        client.force_authenticate(user=setup_data['user'])
        
        response = client.get('/api/sv/mon-hoc-ghi-danh')
        
        assert response.status_code == 200
        assert response.data['isSuccess'] is True
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['maMonHoc'] == "M01"

    def test_ghi_danh_mon_hoc(self, client, setup_data):
        client.force_authenticate(user=setup_data['user'])
        
        hp_id = str(setup_data['hp'].id)
        response = client.post('/api/sv/ghi-danh', {'monHocId': hp_id}, format='json')
        
        assert response.status_code == 200
        assert response.data['isSuccess'] is True
        assert response.data['message'] == "Ghi danh môn học thành công"
        
        # Verify DB
        assert GhiDanhHocPhan.objects.filter(sinh_vien_id=setup_data['user'].id, hoc_phan_id=hp_id).exists()

    def test_get_danh_sach_da_ghi_danh(self, client, setup_data):
        client.force_authenticate(user=setup_data['user'])
        
        # Create existing registration
        GhiDanhHocPhan.objects.create(
            id=uuid.uuid4(),
            sinh_vien_id=setup_data['user'].id,
            hoc_phan=setup_data['hp'],
            trang_thai="da_ghi_danh"
        )
        
        response = client.get('/api/sv/ghi-danh/my')
        
        assert response.status_code == 200
        assert response.data['isSuccess'] is True
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['maMonHoc'] == "M01"
