"""
E2E Tests for PDT Tuition Policy API
Endpoints:
- GET /api/pdt/chinh-sach-tin-chi
- POST /api/pdt/chinh-sach-tin-chi
- PUT /api/pdt/chinh-sach-tin-chi/<id>
- POST /api/pdt/hoc-phi/tinh-toan-hang-loat
"""
import pytest
import uuid
from datetime import date, timedelta
from decimal import Decimal
from rest_framework import status


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTuitionPolicy:
    """E2E tests for Tuition Policy API"""
    
    def test_get_tuition_policies(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT gets list of tuition policies
        
        Given: PDT user authenticated
        When: GET /api/pdt/chinh-sach-tin-chi
        Then: Status 200, list of policies
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        response = api_client.get('/api/pdt/chinh-sach-tin-chi')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_create_tuition_policy_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT creates a new tuition policy
        
        Given: PDT user authenticated
        When: POST /api/pdt/chinh-sach-tin-chi
        Then: Status 200/201, policy created
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        hoc_ky = setup_base_data['hoc_ky']
        khoa = setup_base_data['khoa']
        
        payload = {
            'hocKyId': str(hoc_ky.id),
            'khoaId': str(khoa.id),
            'phiMoiTinChi': 500000,
            'ngayHieuLuc': date.today().isoformat()
        }
        
        response = api_client.post('/api/pdt/chinh-sach-tin-chi', payload, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_update_tuition_policy(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT updates a tuition policy
        
        Given: PDT user authenticated, policy exists
        When: PUT /api/pdt/chinh-sach-tin-chi/<id>
        Then: Status 200, policy updated
        """
        from infrastructure.persistence.models import ChinhSachTinChi
        
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        hoc_ky = setup_base_data['hoc_ky']
        khoa = setup_base_data['khoa']
        
        # Create existing policy
        policy = ChinhSachTinChi.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_ky=hoc_ky,
            khoa=khoa,
            phi_moi_tin_chi=Decimal('500000'),
            ngay_hieu_luc=date.today()
        )
        
        payload = {
            'phiMoiTinChi': 550000
        }
        
        response = api_client.put(f'/api/pdt/chinh-sach-tin-chi/{policy.id}', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestCalculateTuition:
    """E2E tests for Calculate Tuition API"""
    
    def test_calculate_tuition_bulk(self, api_client, setup_base_data, create_pdt_user, create_sv_user):
        """
        Test Case: PDT calculates tuition for multiple students
        
        Given: PDT user authenticated, students with registrations exist
        When: POST /api/pdt/hoc-phi/tinh-toan-hang-loat
        Then: Status 200, tuition calculated
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        hoc_ky = setup_base_data['hoc_ky']
        khoa = setup_base_data['khoa']
        
        # Create student
        sv = create_sv_user()
        
        payload = {
            'hocKyId': str(hoc_ky.id),
            'khoaId': str(khoa.id)
        }
        
        response = api_client.post('/api/pdt/hoc-phi/tinh-toan-hang-loat', payload, format='json')
        
        # May return 200 with 0 calculated if no registrations
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
