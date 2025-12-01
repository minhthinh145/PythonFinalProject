"""
E2E Tests for Auth API
Test-Driven Development - RED Phase
"""


import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from infrastructure.persistence.models import Users, TaiKhoan
import uuid


@pytest.mark.e2e
@pytest.mark.django_db(databases=['neon'], transaction=True)
class TestLoginAPI:
    """
    E2E tests for Login API
    Endpoint: POST /api/auth/login
    """
    
    def test_login_success_with_valid_credentials(self, api_client, create_test_account):
        """
        Test Case 1: Đăng nhập thành công với thông tin hợp lệ
        
        Given: User có tài khoản active trong DB
        When: POST /api/auth/login với username và password đúng
        Then: 
            - Status code = 200
            - Response có token
            - Response có user info
        """
        # Arrange - Tạo test account
        import uuid
        unique_username = f"teststudent_{uuid.uuid4().hex[:8]}"
        
        test_data = create_test_account(
            username=unique_username,
            password='testpass123',
            loai='sinh_vien',
            active=True
        )
        
        login_payload = {
            'tenDangNhap': unique_username,
            'matKhau': 'testpass123'
        }
        
        # Act - Gọi API login
        response = api_client.post('/api/auth/login', login_payload, format='json')
        
        # Assert
        print(f"\nDEBUG: Response Status: {response.status_code}")
        print(f"DEBUG: Response Data: {response.json()}")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['isSuccess'] is True
        assert data['message'] == 'Đăng nhập thành công'
        assert 'data' in data
        assert 'token' in data['data']
        assert 'refreshToken' in data['data']
        assert 'user' in data['data']
        
        # Verify user data structure (map 1-1 frontend User interface)
        user = data['data']['user']
        assert 'id' in user
        assert 'hoTen' in user
        assert 'loaiTaiKhoan' in user
        assert user['loaiTaiKhoan'] == 'sinh_vien'
    
    def test_login_fail_with_wrong_password(self, api_client, create_test_account):
        """
        Test Case 2: Đăng nhập thất bại - sai mật khẩu
        
        Given: User có tài khoản trong DB
        When: POST /api/auth/login với password sai
        Then:
            - Status code = 401
            - Response message: "Tên đăng nhập hoặc mật khẩu không đúng"
        """
        # Arrange
        create_test_account(
            username='testuser2',
            password='correctpass123',
            loai='sinh_vien'
        )
        
        login_payload = {
            'tenDangNhap': 'testuser2',
            'matKhau': 'wrongpassword'
        }
        
        # Act
        response = api_client.post('/api/auth/login', login_payload, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert data['isSuccess'] is False
        assert 'Tên đăng nhập hoặc mật khẩu không đúng' in data['message']
    
    def test_login_fail_with_nonexistent_user(self, api_client):
        """
        Test Case 3: Đăng nhập thất bại - user không tồn tại
        
        Given: Username không tồn tại trong DB
        When: POST /api/auth/login
        Then:
            - Status code = 401
            - Response message: "Tên đăng nhập hoặc mật khẩu không đúng"
        """
        # Arrange
        login_payload = {
            'tenDangNhap': 'nonexistentuser',
            'matKhau': 'anypassword'
        }
        
        # Act
        response = api_client.post('/api/auth/login', login_payload, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert data['isSuccess'] is False
        assert 'Tên đăng nhập hoặc mật khẩu không đúng' in data['message']
    
    def test_login_fail_with_inactive_account(self, api_client, create_test_account):
        """
        Test Case 4: Đăng nhập thất bại - tài khoản bị vô hiệu hóa
        
        Given: User có tài khoản nhưng bị vô hiệu hóa (trang_thai_hoat_dong = False)
        When: POST /api/auth/login
        Then:
            - Status code = 403
            - Response message: "Tài khoản đã bị vô hiệu hóa"
        """
        # Arrange
        create_test_account(
            username='inactiveuser',
            password='testpass123',
            loai='sinh_vien',
            active=False  # Account bị vô hiệu hóa
        )
        
        login_payload = {
            'tenDangNhap': 'inactiveuser',
            'matKhau': 'testpass123'
        }
        
        # Act
        response = api_client.post('/api/auth/login', login_payload, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert data['isSuccess'] is False
        assert 'Tài khoản đã bị vô hiệu hóa' in data['message']
    
    def test_login_fail_with_missing_credentials(self, api_client):
        """
        Test Case 5: Đăng nhập thất bại - thiếu thông tin đăng nhập
        
        Given: Request không có username hoặc password
        When: POST /api/auth/login
        Then:
            - Status code = 400
            - Response message: "Vui lòng cung cấp tên đăng nhập và mật khẩu"
        """
        # Test missing username
        response = api_client.post('/api/auth/login', {'matKhau': 'pass123'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['isSuccess'] is False
        
        # Test missing password
        response = api_client.post('/api/auth/login', {'tenDangNhap': 'user'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['isSuccess'] is False
        
        # Test empty payload
        response = api_client.post('/api/auth/login', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()['isSuccess'] is False


@pytest.mark.e2e
@pytest.mark.django_db(databases=['neon'], transaction=True)
class TestRefreshTokenAPI:
    """
    E2E tests for Refresh Token API
    Endpoint: POST /api/auth/refresh
    """
    
    def test_refresh_token_success(self, api_client, create_test_account):
        """
        Test Case 6: Refresh token thành công
        
        Given: User đã login và có refresh token hợp lệ
        When: POST /api/auth/refresh với refreshToken
        Then:
            - Status code = 200
            - Response có accessToken mới
        """
        # Arrange - Login để lấy refresh token
        create_test_account(username='refreshuser', password='pass123')
        
        login_response = api_client.post('/api/auth/login', {
            'tenDangNhap': 'refreshuser',
            'matKhau': 'pass123'
        }, format='json')
        
        refresh_token = login_response.json()['data']['refreshToken']
        
        # Act - Refresh token
        response = api_client.post('/api/auth/refresh', {
            'refreshToken': refresh_token
        }, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['isSuccess'] is True
        assert 'data' in data
        assert 'accessToken' in data['data']
    
    def test_refresh_token_fail_with_invalid_token(self, api_client):
        """
        Test Case 7: Refresh token thất bại - token không hợp lệ
        
        Given: Refresh token không hợp lệ hoặc đã hết hạn
        When: POST /api/auth/refresh
        Then:
            - Status code = 401
            - Response message: "Invalid or expired refresh token"
        """
        # Act
        response = api_client.post('/api/auth/refresh', {
            'refreshToken': 'invalid_token_abc123'
        }, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert data['isSuccess'] is False
        assert 'Invalid or expired refresh token' in data['message']
    
    def test_refresh_token_fail_with_missing_token(self, api_client):
        """
        Test Case 8: Refresh token thất bại - thiếu token
        
        Given: Request không có refreshToken
        When: POST /api/auth/refresh
        Then:
            - Status code = 400
            - Response message: "Vui lòng cung cấp refresh token"
        """
        # Act
        response = api_client.post('/api/auth/refresh', {}, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data['isSuccess'] is False
        assert 'Vui lòng cung cấp refresh token' in data['message']
