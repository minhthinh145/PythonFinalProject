"""
Domain Layer - Auth DTOs
Map 1-1 với Frontend types
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginDTO:
    """
    Login Request DTO
    Map 1-1: LoginRequest from frontend
    """
    ten_dang_nhap: str  # tenDangNhap
    mat_khau: str       # matKhau
    
    @classmethod
    def from_request(cls, data: dict) -> 'LoginDTO':
        """Create from request data"""
        return cls(
            ten_dang_nhap=data.get('tenDangNhap', ''),
            mat_khau=data.get('matKhau', '')
        )


@dataclass
class RefreshTokenDTO:
    """Refresh Token Request DTO"""
    refresh_token: str
