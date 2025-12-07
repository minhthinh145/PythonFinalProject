"""
E2E Tests for PDT Dot Dang Ky API
Endpoints:
- POST /api/pdt/dot-dang-ky
- GET /api/pdt/dot-dang-ky/<hocKyId>
- PUT /api/pdt/dot-ghi-danh/update
"""
import pytest
import uuid
from datetime import datetime, timedelta
from rest_framework import status
from django.utils import timezone


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestDotDangKy:
    """E2E tests for Dot Dang Ky API"""
    
    def test_create_dot_dang_ky_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT creates a registration period
        
        Given: PDT user authenticated, valid HocKy
        When: POST /api/pdt/dot-dang-ky
        Then: Status 200/201, period created
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        hoc_ky = setup_base_data['hoc_ky']
        now = timezone.now()
        
        payload = {
            'hocKyId': str(hoc_ky.id),
            'loaiDot': 'dang_ky_hoc_phan',
            'gioiHanTinChi': 25,
            'thoiGianBatDau': now.isoformat(),
            'thoiGianKetThuc': (now + timedelta(days=14)).isoformat(),
            'hanHuyDen': (now + timedelta(days=7)).isoformat(),
            'isCheckToanTruong': True
        }
        
        response = api_client.post('/api/pdt/dot-dang-ky', payload, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_get_dot_dang_ky_by_hoc_ky(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT gets registration periods for a semester
        
        Given: PDT user authenticated, dot dang ky exists
        When: GET /api/pdt/dot-dang-ky/<hocKyId>
        Then: Status 200, list of periods returned
        """
        from infrastructure.persistence.models import DotDangKy
        
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        hoc_ky = setup_base_data['hoc_ky']
        now = timezone.now()
        
        # Create test dot dang ky
        DotDangKy.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_ky=hoc_ky,
            loai_dot='dang_ky_hoc_phan',
            gioi_han_tin_chi=25,
            thoi_gian_bat_dau=now,
            thoi_gian_ket_thuc=now + timedelta(days=14),
            is_check_toan_truong=True
        )
        
        response = api_client.get(f'/api/pdt/dot-dang-ky/{hoc_ky.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_update_dot_ghi_danh(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT updates a ghi danh period
        
        Given: PDT user authenticated, dot ghi danh exists
        When: PUT /api/pdt/dot-ghi-danh/update
        Then: Status 200, period updated
        """
        from infrastructure.persistence.models import DotDangKy
        
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        hoc_ky = setup_base_data['hoc_ky']
        now = timezone.now()
        
        # Create test dot ghi danh
        dot = DotDangKy.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_ky=hoc_ky,
            loai_dot='ghi_danh',
            thoi_gian_bat_dau=now,
            thoi_gian_ket_thuc=now + timedelta(days=14),
            is_check_toan_truong=True
        )
        
        new_end = now + timedelta(days=21)
        payload = {
            'id': str(dot.id),
            'thoiGianKetThuc': new_end.isoformat()
        }
        
        response = api_client.put('/api/pdt/dot-ghi-danh/update', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGetDanhSachKhoa:
    """E2E tests for Get Danh Sach Khoa API"""
    
    def test_get_danh_sach_khoa_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT gets list of faculties
        
        Given: PDT user authenticated, khoa exists
        When: GET /api/pdt/khoa
        Then: Status 200, list of khoa returned
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        response = api_client.get('/api/pdt/khoa')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
        assert len(data['data']) >= 1
