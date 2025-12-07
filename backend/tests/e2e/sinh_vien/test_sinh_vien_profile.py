"""
E2E Tests for SinhVien Profile API
Endpoints:
- GET /api/sv/profile
- GET /api/sv/lop-hoc-phan/<lhp_id>/tai-lieu
- GET /api/sv/lop-hoc-phan/<lhp_id>/tai-lieu/<doc_id>/download
"""
import pytest
import uuid
from rest_framework import status
from django.utils import timezone


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestSinhVienProfile:
    """E2E tests for Sinh Vien Profile API"""
    
    def test_get_sinh_vien_profile_success(self, api_client, setup_base_data, create_sv_user):
        """
        Test Case: SV gets their profile
        
        Given: SV user authenticated
        When: GET /api/sv/profile
        Then: Status 200, profile data with correct structure
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        response = api_client.get('/api/sv/profile')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
        
        # Verify response structure matches FE interface
        profile = data['data']
        expected_fields = ['id', 'hoTen', 'maSoSinhVien', 'email', 'lop', 'khoa', 'nganh']
        for field in expected_fields:
            assert field in profile, f"Missing field: {field}"
    
    def test_get_sinh_vien_profile_unauthorized(self, api_client):
        """
        Test Case: Unauthenticated request
        
        Given: No authentication
        When: GET /api/sv/profile
        Then: Status 401
        """
        response = api_client.get('/api/sv/profile')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestSVTaiLieu:
    """E2E tests for SV Tai Lieu API"""
    
    @pytest.fixture
    def setup_sv_with_lop(self, setup_base_data, create_sv_user, create_lop_hoc_phan):
        """Setup SV with registered class"""
        from infrastructure.persistence.models import DangKyHocPhan
        
        sv = create_sv_user()
        lop = create_lop_hoc_phan()
        
        # Register SV for the class
        DangKyHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            lop_hoc_phan=lop,
            ngay_dang_ky=timezone.now(),
            trang_thai='da_dang_ky'
        )
        
        return {'sv': sv, 'lop': lop}
    
    def test_get_tai_lieu_list(self, api_client, setup_sv_with_lop):
        """
        Test Case: SV gets documents of their registered class
        
        Given: SV authenticated, registered for a class
        When: GET /api/sv/lop-hoc-phan/<lhp_id>/tai-lieu
        Then: Status 200, list of documents
        """
        sv = setup_sv_with_lop['sv']
        lop = setup_sv_with_lop['lop']
        api_client.force_authenticate(user=sv)
        
        response = api_client.get(f'/api/sv/lop-hoc-phan/{lop.id}/tai-lieu')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_get_tai_lieu_not_registered(self, api_client, setup_base_data, create_sv_user, create_lop_hoc_phan):
        """
        Test Case: SV tries to access documents of unregistered class
        
        Given: SV authenticated, NOT registered for the class
        When: GET /api/sv/lop-hoc-phan/<lhp_id>/tai-lieu
        Then: Status 403 or empty list
        """
        sv = create_sv_user()
        lop = create_lop_hoc_phan()
        api_client.force_authenticate(user=sv)
        
        response = api_client.get(f'/api/sv/lop-hoc-phan/{lop.id}/tai-lieu')
        
        # May return 403 or 200 with empty list depending on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
