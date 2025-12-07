"""
E2E Tests for PDT De Xuat Hoc Phan API
Endpoints:
- GET /api/pdt/de-xuat-hoc-phan
- PUT /api/pdt/de-xuat-hoc-phan/duyet
- PUT /api/pdt/de-xuat-hoc-phan/tu-choi
"""
import pytest
import uuid
from rest_framework import status
from django.utils import timezone


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestPDTDeXuatHocPhan:
    """E2E tests for PDT De Xuat Hoc Phan API"""
    
    @pytest.fixture
    def setup_de_xuat(self, setup_base_data, create_mon_hoc, create_tlk_user):
        """Setup De Xuat Hoc Phan data"""
        from infrastructure.persistence.models import DeXuatHocPhan, Users
        
        mon_hoc = create_mon_hoc()
        hoc_ky = setup_base_data['hoc_ky']
        khoa = setup_base_data['khoa']
        
        # Get TLK user to be nguoi_tao
        tlk = create_tlk_user()
        
        de_xuat = DeXuatHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            khoa=khoa,
            nguoi_tao_id=tlk.id,
            hoc_ky=hoc_ky,
            mon_hoc=mon_hoc,
            so_lop_du_kien=2,
            trang_thai='da_duyet_tk',  # Already approved by TK
            cap_duyet_hien_tai='pdt',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        return de_xuat
    
    def test_get_de_xuat_list_success(self, api_client, create_pdt_user, setup_de_xuat):
        """
        Test Case: PDT gets list of proposals awaiting approval
        
        Given: PDT user authenticated, de xuat exists with da_duyet_tk status
        When: GET /api/pdt/de-xuat-hoc-phan
        Then: Status 200, list of proposals returned
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        response = api_client.get('/api/pdt/de-xuat-hoc-phan')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_approve_de_xuat_success(self, api_client, create_pdt_user, setup_de_xuat):
        """
        Test Case: PDT approves a proposal
        
        Given: PDT user authenticated, de xuat with da_duyet_tk status
        When: PUT /api/pdt/de-xuat-hoc-phan/duyet
        Then: Status 200, proposal marked as da_duyet_pdt
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        payload = {
            'proposalIds': [str(setup_de_xuat.id)]
        }
        
        response = api_client.put('/api/pdt/de-xuat-hoc-phan/duyet', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        
        # Verify DB state
        from infrastructure.persistence.models import DeXuatHocPhan
        de_xuat = DeXuatHocPhan.objects.using('neon').get(id=setup_de_xuat.id)
        assert de_xuat.trang_thai == 'da_duyet_pdt'
    
    def test_reject_de_xuat_success(self, api_client, create_pdt_user, setup_de_xuat):
        """
        Test Case: PDT rejects a proposal
        
        Given: PDT user authenticated, de xuat exists
        When: PUT /api/pdt/de-xuat-hoc-phan/tu-choi
        Then: Status 200, proposal marked as tu_choi
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        payload = {
            'proposalId': str(setup_de_xuat.id)
        }
        
        response = api_client.put('/api/pdt/de-xuat-hoc-phan/tu-choi', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_approve_non_existent_de_xuat(self, api_client, create_pdt_user):
        """
        Test Case: PDT approves non-existent proposal
        
        Given: PDT user authenticated
        When: PUT with non-existent proposal ID
        Then: Status 404/400, error message
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        payload = {
            'proposalIds': [str(uuid.uuid4())]
        }
        
        response = api_client.put('/api/pdt/de-xuat-hoc-phan/duyet', payload, format='json')
        
        # Should handle gracefully - either 404 or 200 with 0 approved
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
