"""
E2E Tests for GV (Giang Vien) Operations API
Endpoints:
- GET /api/gv/lop-hoc-phan
- GET /api/gv/lop-hoc-phan/<lhp_id>
- GET /api/gv/lop-hoc-phan/<lhp_id>/sinh-vien
- GET/PUT /api/gv/lop-hoc-phan/<lhp_id>/diem
- GET /api/gv/tkb-weekly
- GET /api/gv/lop-hoc-phan/<lhp_id>/tai-lieu
- POST /api/gv/lop-hoc-phan/<lhp_id>/tai-lieu/upload
- GET /api/gv/lop-hoc-phan/<lhp_id>/tai-lieu/<doc_id>/download
"""
import pytest
import uuid
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGVLopHocPhan:
    """E2E tests for GV Lop Hoc Phan API"""
    
    @pytest.fixture
    def setup_gv_lop(self, setup_base_data, create_gv_user, create_hoc_phan):
        """Setup GV with assigned Lop Hoc Phan"""
        from infrastructure.persistence.models import LopHocPhan
        
        gv = create_gv_user()
        hoc_phan = create_hoc_phan()
        
        lop = LopHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_phan=hoc_phan,
            ma_lop=f"LHP_{uuid.uuid4().hex[:6]}",
            giang_vien_id=gv.id,
            so_luong_toi_da=50,
            so_luong_hien_tai=0,
            trang_thai_lop='dang_mo'
        )
        
        return {'gv': gv, 'lop': lop, 'hoc_phan': hoc_phan}
    
    def test_get_lop_hoc_phan_list(self, api_client, setup_gv_lop):
        """
        Test Case: GV gets list of their classes
        
        Given: GV user authenticated, has assigned classes
        When: GET /api/gv/lop-hoc-phan
        Then: Status 200, list of classes
        """
        gv = setup_gv_lop['gv']
        api_client.force_authenticate(user=gv)
        
        response = api_client.get('/api/gv/lop-hoc-phan')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_get_lop_hoc_phan_detail(self, api_client, setup_gv_lop):
        """
        Test Case: GV gets detail of a class
        
        Given: GV user authenticated, class exists
        When: GET /api/gv/lop-hoc-phan/<lhp_id>
        Then: Status 200, class details
        """
        gv = setup_gv_lop['gv']
        lop = setup_gv_lop['lop']
        api_client.force_authenticate(user=gv)
        
        response = api_client.get(f'/api/gv/lop-hoc-phan/{lop.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGVStudents:
    """E2E tests for GV Students API"""
    
    @pytest.fixture
    def setup_gv_with_students(self, setup_base_data, create_gv_user, create_hoc_phan, create_sv_user):
        """Setup GV with class and enrolled students"""
        from infrastructure.persistence.models import LopHocPhan, DangKyHocPhan
        
        gv = create_gv_user()
        hoc_phan = create_hoc_phan()
        
        lop = LopHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_phan=hoc_phan,
            ma_lop=f"LHP_{uuid.uuid4().hex[:6]}",
            giang_vien_id=gv.id,
            so_luong_toi_da=50,
            so_luong_hien_tai=1,
            trang_thai_lop='dang_mo'
        )
        
        sv = create_sv_user()
        
        # Register student
        DangKyHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            lop_hoc_phan=lop,
            ngay_dang_ky=timezone.now(),
            trang_thai='da_dang_ky'
        )
        
        return {'gv': gv, 'lop': lop, 'sv': sv}
    
    def test_get_lop_hoc_phan_students(self, api_client, setup_gv_with_students):
        """
        Test Case: GV gets students of a class
        
        Given: GV user authenticated, students enrolled
        When: GET /api/gv/lop-hoc-phan/<lhp_id>/sinh-vien
        Then: Status 200, list of students
        """
        gv = setup_gv_with_students['gv']
        lop = setup_gv_with_students['lop']
        api_client.force_authenticate(user=gv)
        
        response = api_client.get(f'/api/gv/lop-hoc-phan/{lop.id}/sinh-vien')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGVGrades:
    """E2E tests for GV Grades API"""
    
    @pytest.fixture
    def setup_gv_with_grades(self, setup_base_data, create_gv_user, create_hoc_phan, create_sv_user, create_mon_hoc):
        """Setup GV with class, students, and grades"""
        from infrastructure.persistence.models import (
            LopHocPhan, DangKyHocPhan, KetQuaHocPhan
        )
        
        gv = create_gv_user()
        mon_hoc = create_mon_hoc()
        hoc_phan = create_hoc_phan(mon_hoc)
        hoc_ky = setup_base_data['hoc_ky']
        
        lop = LopHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_phan=hoc_phan,
            ma_lop=f"LHP_{uuid.uuid4().hex[:6]}",
            giang_vien_id=gv.id,
            so_luong_toi_da=50,
            so_luong_hien_tai=1,
            trang_thai_lop='dang_mo'
        )
        
        sv = create_sv_user()
        
        # Register student
        DangKyHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            lop_hoc_phan=lop,
            ngay_dang_ky=timezone.now(),
            trang_thai='da_dang_ky'
        )
        
        # Create grade record
        ket_qua = KetQuaHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sv.id,
            mon_hoc=mon_hoc,
            hoc_ky=hoc_ky,
            lop_hoc_phan=lop,
            diem_so=None,
            trang_thai='chua_co_diem'
        )
        
        return {'gv': gv, 'lop': lop, 'sv': sv, 'mon_hoc': mon_hoc, 'ket_qua': ket_qua}
    
    def test_get_grades(self, api_client, setup_gv_with_grades):
        """
        Test Case: GV gets grades of a class
        
        Given: GV user authenticated, students enrolled
        When: GET /api/gv/lop-hoc-phan/<lhp_id>/diem
        Then: Status 200, list of grades
        """
        gv = setup_gv_with_grades['gv']
        lop = setup_gv_with_grades['lop']
        api_client.force_authenticate(user=gv)
        
        response = api_client.get(f'/api/gv/lop-hoc-phan/{lop.id}/diem')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_update_grades(self, api_client, setup_gv_with_grades):
        """
        Test Case: GV updates grades for a class
        
        Given: GV user authenticated, students enrolled
        When: PUT /api/gv/lop-hoc-phan/<lhp_id>/diem
        Then: Status 200, grades updated
        """
        gv = setup_gv_with_grades['gv']
        lop = setup_gv_with_grades['lop']
        sv = setup_gv_with_grades['sv']
        api_client.force_authenticate(user=gv)
        
        payload = {
            'grades': [
                {
                    'sinhVienId': str(sv.id),
                    'diemSo': 8.5
                }
            ]
        }
        
        response = api_client.put(f'/api/gv/lop-hoc-phan/{lop.id}/diem', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGVTKB:
    """E2E tests for GV TKB API"""
    
    def test_get_tkb_weekly(self, api_client, setup_base_data, create_gv_user):
        """
        Test Case: GV gets weekly schedule
        
        Given: GV user authenticated
        When: GET /api/gv/tkb-weekly
        Then: Status 200, weekly TKB data
        """
        gv = create_gv_user()
        api_client.force_authenticate(user=gv)
        
        response = api_client.get('/api/gv/tkb-weekly')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGVTaiLieu:
    """E2E tests for GV Tai Lieu API"""
    
    @pytest.fixture
    def setup_gv_lop_tailieu(self, setup_base_data, create_gv_user, create_hoc_phan):
        """Setup GV with class for tai lieu"""
        from infrastructure.persistence.models import LopHocPhan
        
        gv = create_gv_user()
        hoc_phan = create_hoc_phan()
        
        lop = LopHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            hoc_phan=hoc_phan,
            ma_lop=f"LHP_{uuid.uuid4().hex[:6]}",
            giang_vien_id=gv.id,
            so_luong_toi_da=50,
            so_luong_hien_tai=0,
            trang_thai_lop='dang_mo'
        )
        
        return {'gv': gv, 'lop': lop}
    
    def test_get_tai_lieu_list(self, api_client, setup_gv_lop_tailieu):
        """
        Test Case: GV gets documents of a class
        
        Given: GV user authenticated
        When: GET /api/gv/lop-hoc-phan/<lhp_id>/tai-lieu
        Then: Status 200, list of documents
        """
        gv = setup_gv_lop_tailieu['gv']
        lop = setup_gv_lop_tailieu['lop']
        api_client.force_authenticate(user=gv)
        
        response = api_client.get(f'/api/gv/lop-hoc-phan/{lop.id}/tai-lieu')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
