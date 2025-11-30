"""
Presentation Layer - Auth API Views
Map 1-1 với frontend API endpoints
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from application.auth import LoginUseCase, RefreshTokenUseCase
from domain.auth.dto import LoginDTO, RefreshTokenDTO
from infrastructure.persistence.auth import AuthRepository


class LoginView(APIView):
    """
    Login API endpoint
    POST /api/auth/login
    Map 1-1: { url: "/auth/login", method: "POST", body }
    """
    
    authentication_classes = [] # ✅ Disable auth to allow invalid tokens (e.g. expired)
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Handle login request
        
        Request body (map 1-1 frontend LoginRequest):
            {
                "tenDangNhap": "string",
                "matKhau": "string"
            }
        
        Response (map 1-1 frontend LoginResponse):
            {
                "isSuccess": true,
                "message": "string",
                "data": {
                    "token": "string",
                    "refreshToken": "string",
                    "user": { ... }
                }
            }
        """
        # Validate request data
        ten_dang_nhap = request.data.get('tenDangNhap')
        mat_khau = request.data.get('matKhau')
        
        if not ten_dang_nhap or not mat_khau:
            return Response(
                {
                    'isSuccess': False,
                    'message': 'Vui lòng cung cấp tên đăng nhập và mật khẩu'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create DTO and execute use case
        dto = LoginDTO(ten_dang_nhap=ten_dang_nhap, mat_khau=mat_khau)
        auth_repository = AuthRepository()
        use_case = LoginUseCase(auth_repository=auth_repository)
        result = use_case.execute(dto)
        
        # Map ServiceResult to HTTP response
        http_status = result.status_code or 200
        
        return Response(result.to_dict(), status=http_status)


class RefreshTokenView(APIView):
    """
    Refresh token API endpoint
    POST /api/auth/refresh
    """
    
    authentication_classes = [] # ✅ Disable auth
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Handle refresh token request
        
        Request body:
            {
                "refreshToken": "string"
            }
        
        Response:
            {
                "isSuccess": true,
                "message": "string",
                "data": {
                    "accessToken": "string"
                }
            }
        """
        refresh_token = request.data.get('refreshToken')
        
        if not refresh_token:
            return Response(
                {
                    'isSuccess': False,
                    'message': 'Vui lòng cung cấp refresh token'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute use case
        dto = RefreshTokenDTO(refresh_token=refresh_token)
        use_case = RefreshTokenUseCase()
        result = use_case.execute(dto)
        
        http_status = result.status_code or 200
        
        return Response(result.to_dict(), status=http_status)
