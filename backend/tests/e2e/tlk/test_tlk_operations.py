"""
E2E Tests for TLK (Tro Ly Khoa) Operations API
Endpoints:
- GET /api/tlk/mon-hoc
- GET /api/tlk/giang-vien
- GET /api/tlk/lop-hoc-phan/get-hoc-phan/<hoc_ky_id>
- GET /api/tlk/phong-hoc
- GET /api/tlk/phong-hoc/available
- POST /api/tlk/de-xuat-hoc-phan
- POST /api/tlk/thoi-khoa-bieu
- GET /api/tlk/thoi-khoa-bieu/batch
"""
import pytest
import uuid
from datetime import datetime, timedelta
from rest_framework import status
from django.utils import timezone


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTLKMonHocGiangVien:
    """E2E tests for TLK Mon Hoc and Giang Vien API"""
    
    def test_get_mon_hoc_by_khoa(self, api_client, setup_base_data, create_tlk_user, create_mon_hoc):
        """
        Test Case: TLK gets subjects of their faculty
        
        Given: TLK user authenticated, subjects exist
        When: GET /api/tlk/mon-hoc
        Then: Status 200, list of subjects for that khoa
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        create_mon_hoc()
        
        response = api_client.get('/api/tlk/mon-hoc')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_get_giang_vien_by_khoa(self, api_client, setup_base_data, create_tlk_user, create_gv_user):
        """
        Test Case: TLK gets lecturers of their faculty
        
        Given: TLK user authenticated, lecturers exist
        When: GET /api/tlk/giang-vien
        Then: Status 200, list of lecturers for that khoa
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        create_gv_user()
        
        response = api_client.get('/api/tlk/giang-vien')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTLKHocPhan:
    """E2E tests for TLK Hoc Phan API"""
    
    def test_get_hoc_phans_for_create_lop(self, api_client, setup_base_data, create_tlk_user):
        """
        Test Case: TLK gets approved hoc phans for creating classes
        
        Given: TLK user authenticated
        When: GET /api/tlk/lop-hoc-phan/get-hoc-phan/<hoc_ky_id>
        Then: Status 200, list of approved hoc phans
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        hoc_ky = setup_base_data['hoc_ky']
        
        response = api_client.get(f'/api/tlk/lop-hoc-phan/get-hoc-phan/{hoc_ky.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTLKPhongHoc:
    """E2E tests for TLK Phong Hoc API"""
    
    def test_get_phong_hoc(self, api_client, setup_base_data, create_tlk_user, create_phong):
        """
        Test Case: TLK gets all rooms of their faculty
        
        Given: TLK user authenticated, rooms exist
        When: GET /api/tlk/phong-hoc
        Then: Status 200, list of rooms
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        create_phong()
        
        response = api_client.get('/api/tlk/phong-hoc')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_get_available_phong_hoc(self, api_client, setup_base_data, create_tlk_user, create_phong):
        """
        Test Case: TLK gets available (unassigned) rooms
        
        Given: TLK user authenticated, unassigned rooms exist
        When: GET /api/tlk/phong-hoc/available
        Then: Status 200, list of available rooms
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        create_phong()  # Creates unassigned room
        
        response = api_client.get('/api/tlk/phong-hoc/available')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTLKDeXuat:
    """E2E tests for TLK De Xuat Hoc Phan API"""
    
    def test_get_de_xuat_list(self, api_client, setup_base_data, create_tlk_user):
        """
        Test Case: TLK gets their de xuat list
        
        Given: TLK user authenticated
        When: GET /api/tlk/de-xuat-hoc-phan
        Then: Status 200, list of de xuat
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        response = api_client.get('/api/tlk/de-xuat-hoc-phan')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_create_de_xuat_hoc_phan(self, api_client, setup_base_data, create_tlk_user, create_mon_hoc, create_gv_user):
        """
        Test Case: TLK creates a new course proposal
        
        Given: TLK user authenticated
        When: POST /api/tlk/de-xuat-hoc-phan
        Then: Status 200/201, de xuat created
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        mon_hoc = create_mon_hoc()
        gv = create_gv_user()
        hoc_ky = setup_base_data['hoc_ky']
        
        payload = {
            'hocKyId': str(hoc_ky.id),
            'monHocId': str(mon_hoc.id),
            'soLopDuKien': 2,
            'giangVienId': str(gv.id)
        }
        
        response = api_client.post('/api/tlk/de-xuat-hoc-phan', payload, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTLKThoiKhoaBieu:
    """E2E tests for TLK Thoi Khoa Bieu API"""
    
    def test_xep_thoi_khoa_bieu(self, api_client, setup_base_data, create_tlk_user, create_mon_hoc, create_phong):
        """
        Test Case: TLK schedules a class
        
        Given: TLK user authenticated, mon hoc and phong exist
        When: POST /api/tlk/thoi-khoa-bieu
        Then: Status 200, TKB created
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        mon_hoc = create_mon_hoc()
        phong = create_phong()
        hoc_ky = setup_base_data['hoc_ky']
        now = timezone.now()
        
        payload = {
            'hocKyId': str(hoc_ky.id),
            'maHocPhan': mon_hoc.ma_mon,
            'danhSachLop': [
                {
                    'tenLop': f'{mon_hoc.ma_mon}_01',
                    'phongHocId': str(phong.id),
                    'ngayBatDau': now.date().isoformat(),
                    'ngayKetThuc': (now + timedelta(days=90)).date().isoformat(),
                    'tietBatDau': 1,
                    'tietKetThuc': 3,
                    'thuTrongTuan': 2
                }
            ]
        }
        
        response = api_client.post('/api/tlk/thoi-khoa-bieu', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_get_tkb_batch(self, api_client, setup_base_data, create_tlk_user, create_mon_hoc):
        """
        Test Case: TLK gets TKB for multiple subjects
        
        Given: TLK user authenticated
        When: GET /api/tlk/thoi-khoa-bieu/batch with maHocPhans
        Then: Status 200, TKB data for requested subjects
        """
        tlk_user = create_tlk_user()
        api_client.force_authenticate(user=tlk_user)
        
        mon_hoc = create_mon_hoc()
        hoc_ky = setup_base_data['hoc_ky']
        
        response = api_client.get(f'/api/tlk/thoi-khoa-bieu/batch?hocKyId={hoc_ky.id}&maHocPhans={mon_hoc.ma_mon}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
