"""
E2E Tests for PDT Hoc Ky Management API
Endpoints:
- PUT /api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh
"""
import pytest
import uuid
from rest_framework import status


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestSetHocKyHienHanh:
    """E2E tests for Set Hoc Ky Hien Hanh API"""
    
    def test_set_hoc_ky_hien_hanh_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT sets current semester successfully
        
        Given: PDT user authenticated, valid HocKy exists
        When: PUT /api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh
        Then: Status 200, HocKy marked as current
        """
        # Arrange
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        hoc_ky = setup_base_data['hoc_ky']
        
        payload = {
            'hocKyId': str(hoc_ky.id)
        }
        
        # Act
        response = api_client.put('/api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh', payload, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'message' in data
    
    def test_set_hoc_ky_hien_hanh_invalid_id(self, api_client, create_pdt_user):
        """
        Test Case: PDT sets invalid HocKy ID
        
        Given: PDT user authenticated
        When: PUT with non-existent HocKy ID
        Then: Status 404, error message
        """
        # Arrange
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        payload = {
            'hocKyId': str(uuid.uuid4())  # Non-existent ID
        }
        
        # Act
        response = api_client.put('/api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh', payload, format='json')
        
        # Assert
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
        data = response.json()
        assert data['isSuccess'] is False
    
    def test_set_hoc_ky_hien_hanh_unauthorized(self, api_client, setup_base_data):
        """
        Test Case: Unauthenticated request
        
        Given: No authentication
        When: PUT /api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh
        Then: Status 401
        """
        payload = {
            'hocKyId': str(setup_base_data['hoc_ky'].id)
        }
        
        response = api_client.put('/api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh', payload, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
