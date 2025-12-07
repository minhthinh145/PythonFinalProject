"""
E2E Tests for Course Registration API
Endpoints:
- GET /api/sv/dkhp/check-phase-dang-ky
- GET /api/sv/dkhp/lop-hoc-phan
- GET /api/sv/dkhp/lop-da-dang-ky
- POST /api/sv/dkhp/dang-ky-hoc-phan
- DELETE /api/sv/dkhp/huy-dang-ky-hoc-phan
- POST /api/sv/dkhp/chuyen-lop-hoc-phan
- GET /api/sv/dkhp/lop-hoc-phan/mon-hoc
- GET /api/sv/dkhp/lich-su-dang-ky
- GET /api/sv/dkhp/tkb-weekly
- GET /api/sv/dkhp/tra-cuu-hoc-phan
- GET /api/sv/dkhp/hoc-phi
"""
import pytest
import uuid
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestCheckPhaseDangKy:
    """E2E tests for Check Phase Dang Ky API"""
    
    def test_check_phase_dang_ky_open(self, api_client, setup_base_data, create_sv_user, create_ky_phase):
        """
        Test Case: Check phase when registration is open
        
        Given: SV user authenticated, dang_ky_hoc_phan phase is enabled
        When: GET /api/sv/dkhp/check-phase-dang-ky
        Then: Status 200, isOpen = True
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        # Create enabled phase
        create_ky_phase('dang_ky_hoc_phan', True)
        
        response = api_client.get('/api/sv/dkhp/check-phase-dang-ky')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_check_phase_dang_ky_closed(self, api_client, setup_base_data, create_sv_user, create_ky_phase):
        """
        Test Case: Check phase when registration is closed
        
        Given: SV user authenticated, dang_ky_hoc_phan phase is disabled
        When: GET /api/sv/dkhp/check-phase-dang-ky
        Then: Status 200, isOpen = False
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        # Create disabled phase
        create_ky_phase('dang_ky_hoc_phan', False)
        
        response = api_client.get('/api/sv/dkhp/check-phase-dang-ky')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGetLopHocPhan:
    """E2E tests for Get Lop Hoc Phan API"""
    
    def test_get_danh_sach_lop_hoc_phan(self, api_client, setup_base_data, create_sv_user, create_lop_hoc_phan, create_ky_phase):
        """
        Test Case: SV gets available classes for registration
        
        Given: SV user authenticated, classes exist
        When: GET /api/sv/dkhp/lop-hoc-phan
        Then: Status 200, list of available classes
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        # Create enabled phase
        create_ky_phase('dang_ky_hoc_phan', True)
        
        # Create a class
        create_lop_hoc_phan()
        
        response = api_client.get('/api/sv/dkhp/lop-hoc-phan')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestDangKyHocPhan:
    """E2E tests for Dang Ky Hoc Phan API"""
    
    @pytest.fixture
    def setup_registration_data(self, setup_base_data, create_sv_user, create_lop_hoc_phan, create_ky_phase):
        """Setup data for registration tests"""
        sv = create_sv_user()
        lop = create_lop_hoc_phan()
        create_ky_phase('dang_ky_hoc_phan', True)
        
        return {'sv': sv, 'lop': lop}
    
    def test_dang_ky_hoc_phan_success(self, api_client, setup_registration_data):
        """
        Test Case: SV registers for a class successfully
        
        Given: SV user authenticated, phase open, class available
        When: POST /api/sv/dkhp/dang-ky-hoc-phan
        Then: Status 200, registration created
        """
        sv = setup_registration_data['sv']
        lop = setup_registration_data['lop']
        api_client.force_authenticate(user=sv)
        
        payload = {
            'lopHocPhanId': str(lop.id)
        }
        
        response = api_client.post('/api/sv/dkhp/dang-ky-hoc-phan', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        
        # Verify registration exists
        from infrastructure.persistence.models import DangKyHocPhan
        assert DangKyHocPhan.objects.using('neon').filter(
            sinh_vien_id=sv.id,
            lop_hoc_phan_id=lop.id
        ).exists()
    
    def test_dang_ky_hoc_phan_already_registered(self, api_client, setup_registration_data):
        """
        Test Case: SV tries to register for already registered class
        
        Given: SV already registered for the class
        When: POST /api/sv/dkhp/dang-ky-hoc-phan
        Then: Status 400, error message
        """
        from infrastructure.persistence.models import DangKyHocPhan
        
        sv = setup_registration_data['sv']
        lop = setup_registration_data['lop']
        api_client.force_authenticate(user=sv)
        
        # Create existing registration
        DangKyHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            lop_hoc_phan=lop,
            ngay_dang_ky=timezone.now(),
            trang_thai='da_dang_ky'
        )
        
        payload = {
            'lopHocPhanId': str(lop.id)
        }
        
        response = api_client.post('/api/sv/dkhp/dang-ky-hoc-phan', payload, format='json')
        
        # Should fail - already registered
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['isSuccess'] is False


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestHuyDangKy:
    """E2E tests for Huy Dang Ky API"""
    
    def test_huy_dang_ky_success(self, api_client, setup_base_data, create_sv_user, create_lop_hoc_phan, create_ky_phase):
        """
        Test Case: SV cancels registration successfully
        
        Given: SV registered for a class
        When: DELETE /api/sv/dkhp/huy-dang-ky-hoc-phan
        Then: Status 200, registration cancelled
        """
        from infrastructure.persistence.models import DangKyHocPhan
        
        sv = create_sv_user()
        lop = create_lop_hoc_phan()
        create_ky_phase('dang_ky_hoc_phan', True)
        api_client.force_authenticate(user=sv)
        
        # Create existing registration
        dang_ky = DangKyHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            lop_hoc_phan=lop,
            ngay_dang_ky=timezone.now(),
            trang_thai='da_dang_ky'
        )
        
        payload = {
            'dangKyIds': [str(dang_ky.id)]
        }
        
        response = api_client.delete('/api/sv/dkhp/huy-dang-ky-hoc-phan', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestChuyenLop:
    """E2E tests for Chuyen Lop API"""
    
    def test_chuyen_lop_success(self, api_client, setup_base_data, create_sv_user, create_hoc_phan, create_ky_phase):
        """
        Test Case: SV switches to another class of same subject
        
        Given: SV registered for a class, another class of same subject exists
        When: POST /api/sv/dkhp/chuyen-lop-hoc-phan
        Then: Status 200, class switched
        """
        from infrastructure.persistence.models import LopHocPhan, DangKyHocPhan
        
        sv = create_sv_user()
        hoc_phan = create_hoc_phan()
        create_ky_phase('dang_ky_hoc_phan', True)
        api_client.force_authenticate(user=sv)
        
        # Create two classes for same subject
        lop1 = LopHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_phan=hoc_phan,
            ma_lop=f"LHP_A_{uuid.uuid4().hex[:4]}",
            so_luong_toi_da=50,
            so_luong_hien_tai=1,
            trang_thai_lop='dang_mo'
        )
        
        lop2 = LopHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_phan=hoc_phan,
            ma_lop=f"LHP_B_{uuid.uuid4().hex[:4]}",
            so_luong_toi_da=50,
            so_luong_hien_tai=0,
            trang_thai_lop='dang_mo'
        )
        
        # Register SV for lop1
        dang_ky = DangKyHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            lop_hoc_phan=lop1,
            ngay_dang_ky=timezone.now(),
            trang_thai='da_dang_ky'
        )
        
        payload = {
            'dangKyId': str(dang_ky.id),
            'lopMoiId': str(lop2.id)
        }
        
        response = api_client.post('/api/sv/dkhp/chuyen-lop-hoc-phan', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGetLopDaDangKy:
    """E2E tests for Get Lop Da Dang Ky API"""
    
    def test_get_danh_sach_lop_da_dang_ky(self, api_client, setup_base_data, create_sv_user, create_lop_hoc_phan):
        """
        Test Case: SV gets list of registered classes
        
        Given: SV has registered classes
        When: GET /api/sv/dkhp/lop-da-dang-ky
        Then: Status 200, list of registered classes
        """
        from infrastructure.persistence.models import DangKyHocPhan
        
        sv = create_sv_user()
        lop = create_lop_hoc_phan()
        api_client.force_authenticate(user=sv)
        
        # Create registration
        DangKyHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            lop_hoc_phan=lop,
            ngay_dang_ky=timezone.now(),
            trang_thai='da_dang_ky'
        )
        
        response = api_client.get('/api/sv/dkhp/lop-da-dang-ky')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestLichSuDangKy:
    """E2E tests for Lich Su Dang Ky API"""
    
    def test_get_lich_su_dang_ky(self, api_client, setup_base_data, create_sv_user):
        """
        Test Case: SV gets registration history
        
        Given: SV user authenticated
        When: GET /api/sv/dkhp/lich-su-dang-ky
        Then: Status 200, registration history
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        response = api_client.get('/api/sv/dkhp/lich-su-dang-ky')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTKBWeekly:
    """E2E tests for TKB Weekly API"""
    
    def test_get_tkb_weekly(self, api_client, setup_base_data, create_sv_user):
        """
        Test Case: SV gets weekly schedule
        
        Given: SV user authenticated
        When: GET /api/sv/dkhp/tkb-weekly
        Then: Status 200, weekly schedule
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        response = api_client.get('/api/sv/dkhp/tkb-weekly')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestHocPhi:
    """E2E tests for Hoc Phi API"""
    
    def test_get_chi_tiet_hoc_phi(self, api_client, setup_base_data, create_sv_user):
        """
        Test Case: SV gets tuition details
        
        Given: SV user authenticated
        When: GET /api/sv/dkhp/hoc-phi
        Then: Status 200, tuition details
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        response = api_client.get('/api/sv/dkhp/hoc-phi')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestTraCuuHocPhan:
    """E2E tests for Tra Cuu Hoc Phan API"""
    
    def test_tra_cuu_hoc_phan(self, api_client, setup_base_data, create_sv_user, create_lop_hoc_phan):
        """
        Test Case: SV searches for classes
        
        Given: SV user authenticated, classes exist
        When: GET /api/sv/dkhp/tra-cuu-hoc-phan
        Then: Status 200, search results
        """
        sv = create_sv_user()
        api_client.force_authenticate(user=sv)
        
        lop = create_lop_hoc_phan()
        
        response = api_client.get('/api/sv/dkhp/tra-cuu-hoc-phan')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
