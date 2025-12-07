"""
E2E Tests for PDT Internal CRUD API
Endpoints:
- GET/POST /api/pdt/sinh-vien
- DELETE /api/pdt/sinh-vien/<id>
- GET/POST /api/pdt/mon-hoc
- DELETE /api/pdt/mon-hoc/<id>
- GET/POST /api/pdt/giang-vien
- DELETE /api/pdt/giang-vien/<id>
"""
import pytest
import uuid
from rest_framework import status


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestSinhVienCRUD:
    """E2E tests for Sinh Vien CRUD API"""
    
    def test_get_sinh_vien_list(self, api_client, setup_base_data, create_pdt_user, create_sv_user):
        """
        Test Case: PDT gets list of students
        
        Given: PDT user authenticated, students exist
        When: GET /api/pdt/sinh-vien
        Then: Status 200, list of students
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        # Create a student
        create_sv_user()
        
        response = api_client.get('/api/pdt/sinh-vien')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_create_sinh_vien_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT creates a new student
        
        Given: PDT user authenticated
        When: POST /api/pdt/sinh-vien
        Then: Status 200/201, student created
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        khoa = setup_base_data['khoa']
        nganh = setup_base_data['nganh']
        unique_id = uuid.uuid4().hex[:8]
        
        payload = {
            'maSoSinhVien': f'SV_NEW_{unique_id}',
            'hoTen': f'Sinh Vien New {unique_id}',
            'email': f'sv_new_{unique_id}@test.com',
            'khoaId': str(khoa.id),
            'nganhId': str(nganh.id),
            'lop': 'KTPM2024',
            'tenDangNhap': f'sv_new_{unique_id}',
            'matKhau': 'test123'
        }
        
        response = api_client.post('/api/pdt/sinh-vien', payload, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_delete_sinh_vien(self, api_client, setup_base_data, create_pdt_user, create_sv_user):
        """
        Test Case: PDT deletes a student
        
        Given: PDT user authenticated, student exists
        When: DELETE /api/pdt/sinh-vien/<id>
        Then: Status 200, student deleted
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        sv = create_sv_user()
        
        response = api_client.delete(f'/api/pdt/sinh-vien/{sv.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestMonHocCRUD:
    """E2E tests for Mon Hoc CRUD API"""
    
    def test_get_mon_hoc_list(self, api_client, setup_base_data, create_pdt_user, create_mon_hoc):
        """
        Test Case: PDT gets list of subjects
        
        Given: PDT user authenticated, subjects exist
        When: GET /api/pdt/mon-hoc
        Then: Status 200, list of subjects
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        create_mon_hoc()
        
        response = api_client.get('/api/pdt/mon-hoc')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_create_mon_hoc_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT creates a new subject
        
        Given: PDT user authenticated
        When: POST /api/pdt/mon-hoc
        Then: Status 200/201, subject created
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        khoa = setup_base_data['khoa']
        unique_id = uuid.uuid4().hex[:6]
        
        payload = {
            'maMon': f'MH_NEW_{unique_id}',
            'tenMon': f'Môn học mới {unique_id}',
            'soTinChi': 3,
            'khoaId': str(khoa.id)
        }
        
        response = api_client.post('/api/pdt/mon-hoc', payload, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_delete_mon_hoc(self, api_client, setup_base_data, create_pdt_user, create_mon_hoc):
        """
        Test Case: PDT deletes a subject
        
        Given: PDT user authenticated, subject exists
        When: DELETE /api/pdt/mon-hoc/<id>
        Then: Status 200, subject deleted
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        mon_hoc = create_mon_hoc()
        
        response = api_client.delete(f'/api/pdt/mon-hoc/{mon_hoc.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True


@pytest.mark.e2e
@pytest.mark.django_db(databases=['default', 'neon'], transaction=True)
class TestGiangVienCRUD:
    """E2E tests for Giang Vien CRUD API"""
    
    def test_get_giang_vien_list(self, api_client, setup_base_data, create_pdt_user, create_gv_user):
        """
        Test Case: PDT gets list of lecturers
        
        Given: PDT user authenticated, lecturers exist
        When: GET /api/pdt/giang-vien
        Then: Status 200, list of lecturers
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        create_gv_user()
        
        response = api_client.get('/api/pdt/giang-vien')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
    
    def test_create_giang_vien_success(self, api_client, setup_base_data, create_pdt_user):
        """
        Test Case: PDT creates a new lecturer
        
        Given: PDT user authenticated
        When: POST /api/pdt/giang-vien
        Then: Status 200/201, lecturer created
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        khoa = setup_base_data['khoa']
        unique_id = uuid.uuid4().hex[:8]
        
        payload = {
            'hoTen': f'Giảng viên mới {unique_id}',
            'email': f'gv_new_{unique_id}@test.com',
            'khoaId': str(khoa.id),
            'chuyenMon': 'Computer Science',
            'trinhDo': 'Tiến sĩ',
            'tenDangNhap': f'gv_new_{unique_id}',
            'matKhau': 'test123'
        }
        
        response = api_client.post('/api/pdt/giang-vien', payload, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data['isSuccess'] is True
    
    def test_delete_giang_vien(self, api_client, setup_base_data, create_pdt_user, create_gv_user):
        """
        Test Case: PDT deletes a lecturer
        
        Given: PDT user authenticated, lecturer exists
        When: DELETE /api/pdt/giang-vien/<id>
        Then: Status 200, lecturer deleted
        """
        pdt_user = create_pdt_user()
        api_client.force_authenticate(user=pdt_user)
        
        gv = create_gv_user()
        
        response = api_client.delete(f'/api/pdt/giang-vien/{gv.id}')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isSuccess'] is True
