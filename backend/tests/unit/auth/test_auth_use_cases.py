"""
Comprehensive tests for Auth module use cases
Tests: LoginUseCase, RefreshTokenUseCase
"""
import pytest
from unittest.mock import MagicMock, patch

from application.auth.login_use_case import LoginUseCase
from application.auth.refresh_token_use_case import RefreshTokenUseCase
from domain.auth.dto import LoginDTO, RefreshTokenDTO


# ==================== FIXTURES ====================

@pytest.fixture
def mock_auth_repo():
    return MagicMock()


@pytest.fixture
def mock_password_service():
    return MagicMock()


@pytest.fixture
def mock_jwt_service():
    return MagicMock()


@pytest.fixture
def mock_tai_khoan():
    """Mock TaiKhoan model instance"""
    account = MagicMock()
    account.id = "acc-001"
    account.mat_khau = "hashed_password"
    account.trang_thai_hoat_dong = True
    account.loai_tai_khoan = "sinh_vien"
    return account


@pytest.fixture
def mock_user():
    """Mock User model instance"""
    user = MagicMock()
    user.id = "user-001"
    user.ho_ten = "Nguyễn Văn A"
    user.ma_nhan_vien = "NV001"
    return user


@pytest.fixture
def login_dto():
    """Create login DTO"""
    return LoginDTO(ten_dang_nhap="student001", mat_khau="password123")


# ==================== LoginUseCase Tests ====================

class TestLoginUseCase:
    """Tests for LoginUseCase"""
    
    def test_login_success_sinh_vien(self, mock_auth_repo, mock_password_service, mock_jwt_service, 
                                      mock_tai_khoan, mock_user, login_dto):
        """Test successful login for sinh_vien"""
        # Arrange
        mock_auth_repo.find_account_by_username.return_value = mock_tai_khoan
        mock_auth_repo.get_user_by_account_id.return_value = mock_user
        mock_auth_repo.get_student_info.return_value = {
            'ma_so_sinh_vien': 'SV001',
            'lop': 'CNTT-K19'
        }
        
        mock_password_service.verify_password.return_value = True
        mock_jwt_service.generate_tokens.return_value = {
            'accessToken': 'access_token_123',
            'refreshToken': 'refresh_token_456'
        }
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        result = use_case.execute(login_dto)
        
        # Assert
        assert result.success is True
        assert result.data['token'] == 'access_token_123'
        assert result.data['refreshToken'] == 'refresh_token_456'
        assert 'user' in result.data
    
    def test_login_success_giang_vien(self, mock_auth_repo, mock_password_service, mock_jwt_service,
                                       mock_tai_khoan, mock_user, login_dto):
        """Test successful login for giang_vien"""
        # Arrange
        mock_tai_khoan.loai_tai_khoan = "giang_vien"
        mock_auth_repo.find_account_by_username.return_value = mock_tai_khoan
        mock_auth_repo.get_user_by_account_id.return_value = mock_user
        
        mock_password_service.verify_password.return_value = True
        mock_jwt_service.generate_tokens.return_value = {
            'accessToken': 'gv_access_token',
            'refreshToken': 'gv_refresh_token'
        }
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        result = use_case.execute(login_dto)
        
        # Assert
        assert result.success is True
        mock_jwt_service.generate_tokens.assert_called_with(
            user_id=str(mock_user.id),
            role="giang_vien"
        )
    
    def test_login_account_not_found(self, mock_auth_repo, mock_password_service, mock_jwt_service, login_dto):
        """Test login with non-existent account"""
        # Arrange
        mock_auth_repo.find_account_by_username.return_value = None
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        result = use_case.execute(login_dto)
        
        # Assert
        assert result.success is False
        assert result.status_code == 401
        assert "Tên đăng nhập hoặc mật khẩu không đúng" in result.message
    
    def test_login_wrong_password(self, mock_auth_repo, mock_password_service, mock_jwt_service,
                                   mock_tai_khoan, login_dto):
        """Test login with wrong password"""
        # Arrange
        mock_auth_repo.find_account_by_username.return_value = mock_tai_khoan
        mock_password_service.verify_password.return_value = False
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        result = use_case.execute(login_dto)
        
        # Assert
        assert result.success is False
        assert result.status_code == 401
    
    def test_login_account_disabled(self, mock_auth_repo, mock_password_service, mock_jwt_service,
                                     mock_tai_khoan, login_dto):
        """Test login with disabled account"""
        # Arrange
        mock_tai_khoan.trang_thai_hoat_dong = False
        mock_auth_repo.find_account_by_username.return_value = mock_tai_khoan
        mock_password_service.verify_password.return_value = True
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        result = use_case.execute(login_dto)
        
        # Assert
        assert result.success is False
        assert result.status_code == 403
        assert "vô hiệu hóa" in result.message
    
    def test_login_user_not_found(self, mock_auth_repo, mock_password_service, mock_jwt_service,
                                   mock_tai_khoan, login_dto):
        """Test login when user info not found"""
        # Arrange
        mock_auth_repo.find_account_by_username.return_value = mock_tai_khoan
        mock_auth_repo.get_user_by_account_id.return_value = None
        mock_password_service.verify_password.return_value = True
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        result = use_case.execute(login_dto)
        
        # Assert
        assert result.success is False
        assert result.status_code == 404


# ==================== RefreshTokenUseCase Tests ====================

class TestRefreshTokenUseCase:
    """Tests for RefreshTokenUseCase"""
    
    def test_refresh_token_success(self, mock_jwt_service):
        """Test successful token refresh"""
        # Arrange
        mock_jwt_service.refresh_access_token.return_value = "new_access_token_789"
        
        use_case = RefreshTokenUseCase(mock_jwt_service)
        dto = RefreshTokenDTO(refresh_token="valid_refresh_token")
        
        # Act
        result = use_case.execute(dto)
        
        # Assert
        assert result.success is True
        assert result.data['accessToken'] == "new_access_token_789"
        mock_jwt_service.refresh_access_token.assert_called_with("valid_refresh_token")
    
    def test_refresh_token_invalid(self, mock_jwt_service):
        """Test refresh with invalid token"""
        # Arrange
        mock_jwt_service.refresh_access_token.side_effect = Exception("Invalid token")
        
        use_case = RefreshTokenUseCase(mock_jwt_service)
        dto = RefreshTokenDTO(refresh_token="invalid_token")
        
        # Act
        result = use_case.execute(dto)
        
        # Assert
        assert result.success is False
        assert result.status_code == 401
    
    def test_refresh_token_expired(self, mock_jwt_service):
        """Test refresh with expired token"""
        # Arrange
        mock_jwt_service.refresh_access_token.side_effect = Exception("Token expired")
        
        use_case = RefreshTokenUseCase(mock_jwt_service)
        dto = RefreshTokenDTO(refresh_token="expired_token")
        
        # Act
        result = use_case.execute(dto)
        
        # Assert
        assert result.success is False
        assert "expired" in result.message.lower()


# ==================== Build User Entity Tests ====================

class TestBuildUserEntity:
    """Tests for _build_user_entity method"""
    
    def test_build_user_entity_sinh_vien(self, mock_auth_repo, mock_password_service, mock_jwt_service,
                                          mock_tai_khoan, mock_user):
        """Test building user entity for sinh_vien"""
        # Arrange
        mock_tai_khoan.loai_tai_khoan = "sinh_vien"
        mock_auth_repo.get_student_info.return_value = {
            'ma_so_sinh_vien': 'SV001',
            'lop': 'CNTT-K19'
        }
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        entity = use_case._build_user_entity(mock_user, mock_tai_khoan)
        
        # Assert
        assert entity.ho_ten == "Nguyễn Văn A"
        assert entity.loai_tai_khoan == "sinh_vien"
        mock_auth_repo.get_student_info.assert_called_once()
    
    def test_build_user_entity_giang_vien(self, mock_auth_repo, mock_password_service, mock_jwt_service,
                                           mock_tai_khoan, mock_user):
        """Test building user entity for giang_vien"""
        # Arrange
        mock_tai_khoan.loai_tai_khoan = "giang_vien"
        
        use_case = LoginUseCase(mock_auth_repo, mock_password_service, mock_jwt_service)
        
        # Act
        entity = use_case._build_user_entity(mock_user, mock_tai_khoan)
        
        # Assert
        assert entity.loai_tai_khoan == "giang_vien"


# ==================== DTO Validation Tests ====================

class TestLoginDTO:
    """Tests for LoginDTO validation"""
    
    def test_create_login_dto(self):
        """Test creating LoginDTO"""
        dto = LoginDTO(ten_dang_nhap="user123", mat_khau="pass456")
        assert dto.ten_dang_nhap == "user123"
        assert dto.mat_khau == "pass456"
    
    def test_create_refresh_token_dto(self):
        """Test creating RefreshTokenDTO"""
        dto = RefreshTokenDTO(refresh_token="token_abc")
        assert dto.refresh_token == "token_abc"
