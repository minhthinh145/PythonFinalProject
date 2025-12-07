"""
E2E Tests for TK (Truong Khoa) De Xuat API
Endpoints:
- GET /api/tk/de-xuat-hoc-phan
- PUT /api/tk/de-xuat-hoc-phan/duyet
- PUT /api/tk/de-xuat-hoc-phan/tu-choi
"""
import pytest
import uuid
from rest_framework import status
from django.utils import timezone


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTKDeXuatHocPhan:
    """E2E tests for TK De Xuat Hoc Phan API"""
    
    @pytest.fixture
    def setup_de_xuat_for_tk(self, setup_base_data, create_mon_hoc, create_tlk_user):
        """Setup De Xuat Hoc Phan data awaiting TK approval"""
        from infrastructure.persistence.models import DeXuatHocPhan
        
        mon_hoc = create_mon_hoc()
        hoc_ky = setup_base_data['hoc_ky']
        khoa = setup_base_data['khoa']
        tlk = create_tlk_user()
        
        de_xuat = DeXuatHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            khoa=khoa,
            nguoi_tao_id=tlk.id,
            hoc_ky=hoc_ky,
            mon_hoc=mon_hoc,
            so_lop_du_kien=2,
            trang_thai='cho_duyet',  # Awaiting TK approval
            cap_duyet_hien_tai='truong_khoa',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        return de_xuat
    
    def test_get_de_xuat_for_truong_khoa(self, api_client, create_tk_user, setup_de_xuat_for_tk):
        """
        Test Case: TK gets list of proposals awaiting approval
        
        Given: TK user authenticated, de xuat exists with cho_duyet status
        When: GET /api/tk/de-xuat-hoc-phan
        Then: Status 200, list of proposals returned
        """
        tk_user = create_tk_user()
        api_client.force_authenticate(user=tk_user)
        
        response = api_client.get('/api/tk/de-xuat-hoc-phan')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_duyet_de_xuat_success(self, api_client, create_tk_user, setup_de_xuat_for_tk):
        """
        Test Case: TK approves a proposal
        
        Given: TK user authenticated, de xuat with cho_duyet status
        When: PUT /api/tk/de-xuat-hoc-phan/duyet
        Then: Status 200, proposal marked as da_duyet_tk
        """
        tk_user = create_tk_user()
        api_client.force_authenticate(user=tk_user)
        
        payload = {
            'proposalIds': [str(setup_de_xuat_for_tk.id)]
        }
        
        response = api_client.put('/api/tk/de-xuat-hoc-phan/duyet', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        
        # Verify DB state
        from infrastructure.persistence.models import DeXuatHocPhan
        de_xuat = DeXuatHocPhan.objects.using('neon').get(id=setup_de_xuat_for_tk.id)
        assert de_xuat.trang_thai == 'da_duyet_tk'
    
    def test_tu_choi_de_xuat_success(self, api_client, create_tk_user, setup_de_xuat_for_tk):
        """
        Test Case: TK rejects a proposal
        
        Given: TK user authenticated, de xuat exists
        When: PUT /api/tk/de-xuat-hoc-phan/tu-choi
        Then: Status 200, proposal marked as tu_choi
        """
        tk_user = create_tk_user()
        api_client.force_authenticate(user=tk_user)
        
        payload = {
            'proposalIds': [str(setup_de_xuat_for_tk.id)]
        }
        
        response = api_client.put('/api/tk/de-xuat-hoc-phan/tu-choi', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_get_de_xuat_unauthorized(self, api_client, setup_de_xuat_for_tk):
        """
        Test Case: Unauthenticated request
        
        Given: No authentication
        When: GET /api/tk/de-xuat-hoc-phan
        Then: Status 401
        """
        response = api_client.get('/api/tk/de-xuat-hoc-phan')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_duyet_de_xuat_non_existent(self, api_client, create_tk_user):
        """
        Test Case: TK approves non-existent proposal
        
        Given: TK user authenticated
        When: PUT with non-existent proposal ID
        Then: Handle gracefully
        """
        tk_user = create_tk_user()
        api_client.force_authenticate(user=tk_user)
        
        payload = {
            'proposalIds': [str(uuid.uuid4())]
        }
        
        response = api_client.put('/api/tk/de-xuat-hoc-phan/duyet', payload, format='json')
        
        # Should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
