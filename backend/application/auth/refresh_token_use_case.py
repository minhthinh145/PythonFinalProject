"""
Application Layer - Refresh Token Use Case
"""
from core.types import ServiceResult
from core.utils import JWTService
from domain.auth.dto import RefreshTokenDTO


class RefreshTokenUseCase:
    """Refresh access token use case"""
    
    def __init__(self, jwt_service: JWTService = None):
        self.jwt_service = jwt_service or JWTService()
    
    def execute(self, dto: RefreshTokenDTO) -> ServiceResult:
        """
        Execute refresh token use case
        
        Args:
            dto: Refresh token DTO
            
        Returns:
            ServiceResult with new access token
        """
        try:
            # Generate new access token from refresh token
            new_access_token = self.jwt_service.refresh_access_token(dto.refresh_token)
            
            return ServiceResult.ok({
                'accessToken': new_access_token
            }, message="Token refreshed successfully")
            
        except Exception as e:
            return ServiceResult.unauthorized(f"Invalid or expired refresh token: {str(e)}")
