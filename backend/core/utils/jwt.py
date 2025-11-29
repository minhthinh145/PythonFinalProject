"""
Core Utils - JWT Service
JWT token generation and validation using SimpleJWT
"""
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Dict


class JWTService:
    """JWT token service using Django REST Framework SimpleJWT"""
    
    @staticmethod
    def generate_tokens(user_id: str, role: str) -> Dict[str, str]:
        """
        Generate access and refresh tokens
        Map 1-1 với BE cũ: { accessToken, refreshToken }
        
        Args:
            user_id: User UUID
            role: User role (sinh_vien, giang_vien, etc.)
            
        Returns:
            Dict with accessToken and refreshToken
        """
        refresh = RefreshToken()
        
        # Add custom claims
        refresh['user_id'] = str(user_id)
        refresh['role'] = role
        
        return {
            'accessToken': str(refresh.access_token),
            'refreshToken': str(refresh),
        }
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """
        Decode and validate JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload with user_id and role
            
        Raises:
            TokenError: If token is invalid or expired
        """
        from rest_framework_simplejwt.tokens import AccessToken
        
        access_token = AccessToken(token)
        return {
            'user_id': access_token['user_id'],
            'role': access_token['role'],
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Generate new access token from refresh token
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            New access token
            
        Raises:
            TokenError: If refresh token is invalid
        """
        refresh = RefreshToken(refresh_token)
        return str(refresh.access_token)
