"""
E2E Tests for PDT Ky Phase API
Endpoints:
- POST /api/pdt/quan-ly-hoc-ky/ky-phase/bulk
- GET /api/pdt/quan-ly-hoc-ky/ky-phase/<hocKyId>
- POST /api/pdt/ky-phase/toggle
"""
import pytest
import uuid
from datetime import datetime, timedelta
from rest_framework import status


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestCreateBulkKyPhase:
    """E2E tests for Create Bulk Ky Phase API"""
    
    def test_create_bulk_ky_phase_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT creates multiple phases for a semester
        
        Given: PDT user authenticated, valid HocKy
        When: POST /api/pdt/quan-ly-hoc-ky/ky-phase/bulk
        Then: Status 200, phases created
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        hoc_ky = setup_base_data['hoc_ky']
        
        now = datetime.now()
        payload = {
            'hocKyId': str(hoc_ky.id),
            'phases': [
                {
                    'phase': 'de_xuat_phe_duyet',
                    'startAt': now.isoformat(),
                    'endAt': (now + timedelta(days=14)).isoformat()
                },
                {
                    'phase': 'ghi_danh',
                    'startAt': (now + timedelta(days=15)).isoformat(),
                    'endAt': (now + timedelta(days=30)).isoformat()
                },
                {
                    'phase': 'dang_ky_hoc_phan',
                    'startAt': (now + timedelta(days=31)).isoformat(),
                    'endAt': (now + timedelta(days=45)).isoformat()
                }
            ]
        }
        
        response = api_client.post('/api/pdt/quan-ly-hoc-ky/ky-phase/bulk', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_create_bulk_ky_phase_invalid_hoc_ky(self, api_client, create_pdt_user):
        """
        Test Case: Create phases for non-existent HocKy
        
        Given: PDT user authenticated
        When: POST with invalid HocKy ID
        Then: Status 404/400, error message
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        now = datetime.now()
        payload = {
            'hocKyId': str(uuid.uuid4()),
            'phases': [
                {
                    'phase': 'ghi_danh',
                    'startAt': now.isoformat(),
                    'endAt': (now + timedelta(days=14)).isoformat()
                }
            ]
        }
        
        response = api_client.post('/api/pdt/quan-ly-hoc-ky/ky-phase/bulk', payload, format='json')
        
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGetPhasesByHocKy:
    """E2E tests for Get Phases By Hoc Ky API"""
    
    def test_get_phases_by_hoc_ky_success(self, api_client, setup_base_data, create_pdt_user, create_ky_phase):
        """
        Test Case: Get all phases for a semester
        
        Given: PDT user authenticated, phases exist
        When: GET /api/pdt/quan-ly-hoc-ky/ky-phase/<hocKyId>
        Then: Status 200, list of phases returned
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        # Create some phases
        create_ky_phase('ghi_danh', True)
        create_ky_phase('dang_ky_hoc_phan', False)
        
        hoc_ky = setup_base_data['hoc_ky']
        
        response = api_client.get(f'/api/pdt/quan-ly-hoc-ky/ky-phase/{hoc_ky.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
        assert 'phases' in data['data']
        assert len(data['data']['phases']) >= 2
    
    def test_get_phases_empty_hoc_ky(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: Get phases for HocKy with no phases
        
        Given: PDT user authenticated, HocKy has no phases
        When: GET /api/pdt/quan-ly-hoc-ky/ky-phase/<hocKyId>
        Then: Status 200, empty list
        """
        from infrastructure.persistence.models import HocKy, NienKhoa
        
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        # Create a new HocKy without phases
        nk = setup_base_data['nien_khoa']
        new_hk = HocKy.objects.using('neon').create(
            id=uuid.uuid4(),
            ten_hoc_ky="HK Empty",
            ma_hoc_ky="HK_EMPTY",
            id_nien_khoa=nk,
            trang_thai_hien_tai=False
        )
        
        response = api_client.get(f'/api/pdt/quan-ly-hoc-ky/ky-phase/{new_hk.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTogglePhase:
    """E2E tests for Toggle Phase API"""
    
    def test_toggle_phase_enable(self, api_client, setup_base_data, create_pdt_user, create_ky_phase):
        """
        Test Case: Toggle phase to enabled
        
        Given: PDT user authenticated, phase exists and disabled
        When: POST /api/pdt/ky-phase/toggle
        Then: Status 200, phase enabled
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        phase = create_ky_phase('ghi_danh', False)
        hoc_ky = setup_base_data['hoc_ky']
        
        payload = {
            'hocKyId': str(hoc_ky.id),
            'phase': 'ghi_danh'
        }
        
        response = api_client.post('/api/pdt/ky-phase/toggle', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_toggle_phase_disable(self, api_client, setup_base_data, create_pdt_user, create_ky_phase):
        """
        Test Case: Toggle phase to disabled
        
        Given: PDT user authenticated, phase exists and enabled
        When: POST /api/pdt/ky-phase/toggle
        Then: Status 200, phase disabled
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        phase = create_ky_phase('dang_ky_hoc_phan', True)
        hoc_ky = setup_base_data['hoc_ky']
        
        payload = {
            'hocKyId': str(hoc_ky.id),
            'phase': 'dang_ky_hoc_phan'
        }
        
        response = api_client.post('/api/pdt/ky-phase/toggle', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
