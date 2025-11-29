"""
Application Layer - Login Use Case
Business logic for user authentication
"""
from typing import Optional

from core.types import ServiceResult
from core.utils import PasswordService, JWTService
from domain.auth.dto import LoginDTO
from domain.auth.entities import UserEntity
from domain.auth.interfaces import IAuthRepository


class LoginUseCase:
    """
    Login use case - map 1-1 logic với BE cũ
    Returns ServiceResult<LoginResponse>
    """
    
    def __init__(
        self,
        auth_repository: IAuthRepository,
        password_service: Optional[PasswordService] = None,
        jwt_service: Optional[JWTService] = None
    ):
        self.auth_repository = auth_repository
        self.password_service = password_service or PasswordService()
        self.jwt_service = jwt_service or JWTService()
    
    def execute(self, dto: LoginDTO) -> ServiceResult:
        """
        Execute login use case
        
        Args:
            dto: Login credentials
            
        Returns:
            ServiceResult with token and user info
            Map 1-1: { success, message, data: { token, user } }
        """
        # 1. Find account by username
        tai_khoan = self.auth_repository.find_account_by_username(dto.ten_dang_nhap)
        
        if not tai_khoan:
            return ServiceResult.unauthorized("Tên đăng nhập hoặc mật khẩu không đúng")
        
        # 2. Verify password
        if not self.password_service.verify_password(dto.mat_khau, tai_khoan.mat_khau):
            return ServiceResult.unauthorized("Tên đăng nhập hoặc mật khẩu không đúng")
        
        # 3. Check if account is active
        if not tai_khoan.trang_thai_hoat_dong:
            return ServiceResult.forbidden("Tài khoản đã bị vô hiệu hóa")
        
        # 4. Get user information
        user = self.auth_repository.get_user_by_account_id(tai_khoan.id)
        
        if not user:
            return ServiceResult.fail("Không tìm thấy thông tin người dùng", 404)
        
        # 5. Build user entity
        user_entity = self._build_user_entity(user, tai_khoan)
        
        # 6. Generate JWT token
        tokens = self.jwt_service.generate_tokens(
            user_id=str(user.id),
            role=tai_khoan.loai_tai_khoan
        )
        
        # 7. Return success result - map 1-1 frontend LoginResponse
        return ServiceResult.ok({
            'token': tokens['accessToken'],
            'refreshToken': tokens['refreshToken'],  # Thêm refresh token
            'user': user_entity.to_dict()
        }, message="Đăng nhập thành công")
    
    def _build_user_entity(self, user, tai_khoan) -> UserEntity:
        """
        Build user entity with role-specific data
        
        Args:
            user: Users model instance
            tai_khoan: TaiKhoan model instance
            
        Returns:
            UserEntity with complete information
        """
        user_data = {
            'id': str(user.id),
            'ho_ten': user.ho_ten,
            'loai_tai_khoan': tai_khoan.loai_tai_khoan,
            'ma_nhan_vien': user.ma_nhan_vien,
        }
        
        # Get student-specific info
        if tai_khoan.loai_tai_khoan == 'sinh_vien':
            student_info = self.auth_repository.get_student_info(user.id)
            if student_info:
                user_data['mssv'] = student_info.get('ma_so_sinh_vien')
                user_data['lop'] = student_info.get('lop')
                user_data['nganh'] = student_info.get('nganh')
        
        return UserEntity(**user_data)
