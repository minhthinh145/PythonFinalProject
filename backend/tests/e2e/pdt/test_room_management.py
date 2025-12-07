"""
E2E Tests for PDT Room Management API
Endpoints:
- GET /api/pdt/phong-hoc/available
- GET /api/pdt/phong-hoc/khoa/<khoaId>
- POST /api/pdt/phong-hoc/assign
- POST /api/pdt/phong-hoc/unassign
"""
import pytest
import uuid
from rest_framework import status


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestRoomManagement:
    """E2E tests for PDT Room Management API"""
    
    def test_get_available_rooms(self, api_client, setup_base_data, create_pdt_user, create_phong):
        """
        Test Case: PDT gets available rooms
        
        Given: PDT user authenticated, unassigned rooms exist
        When: GET /api/pdt/phong-hoc/available
        Then: Status 200, list of available rooms
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        # Create unassigned rooms
        create_phong()
        create_phong()
        
        response = api_client.get('/api/pdt/phong-hoc/available')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_get_rooms_by_khoa(self, api_client, setup_base_data, create_pdt_user, create_phong):
        """
        Test Case: PDT gets rooms by faculty
        
        Given: PDT user authenticated, rooms exist for khoa
        When: GET /api/pdt/phong-hoc/khoa/<khoaId>
        Then: Status 200, list of rooms for that khoa
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        khoa = setup_base_data['khoa']
        create_phong()
        
        response = api_client.get(f'/api/pdt/phong-hoc/khoa/{khoa.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_assign_room_success(self, api_client, setup_base_data, create_pdt_user, create_phong):
        """
        Test Case: PDT assigns room to faculty
        
        Given: PDT user authenticated, unassigned room exists
        When: POST /api/pdt/phong-hoc/assign
        Then: Status 200, room assigned to khoa
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        phong = create_phong()
        khoa = setup_base_data['khoa']
        
        payload = {
            'phongId': str(phong.id),
            'khoaId': str(khoa.id)
        }
        
        response = api_client.post('/api/pdt/phong-hoc/assign', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_unassign_room_success(self, api_client, setup_base_data, create_pdt_user, create_phong):
        """
        Test Case: PDT unassigns room from faculty
        
        Given: PDT user authenticated, assigned room exists
        When: POST /api/pdt/phong-hoc/unassign
        Then: Status 200, room unassigned
        """
        from infrastructure.persistence.models import Phong
        
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        phong = create_phong()
        # Mark room as assigned
        phong.da_dc_su_dung = True
        phong.save(using='neon')
        
        payload = {
            'phongId': str(phong.id)
        }
        
        response = api_client.post('/api/pdt/phong-hoc/unassign', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        
        # Verify room is unassigned
        phong.refresh_from_db(using='neon')
        assert phong.da_dc_su_dung is False
    
    def test_assign_room_invalid_id(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT assigns non-existent room
        
        Given: PDT user authenticated
        When: POST with invalid room ID
        Then: Status 404/400, error message
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        khoa = setup_base_data['khoa']
        
        payload = {
            'phongId': str(uuid.uuid4()),
            'khoaId': str(khoa.id)
        }
        
        response = api_client.post('/api/pdt/phong-hoc/assign', payload, format='json')
        
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
