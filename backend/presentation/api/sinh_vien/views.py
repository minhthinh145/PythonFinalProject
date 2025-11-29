"""
Presentation Layer - SinhVien API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from application.sinh_vien.use_cases import GetSinhVienInfoUseCase
from infrastructure.persistence.sinh_vien import SinhVienRepository

class SinhVienProfileView(APIView):
    """
    Get student profile
    GET /api/sv/profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get current student profile
        """
        # Get user_id from token (request.user is set by DRF authentication)
        # Assuming request.user.id is the UUID
        user_id = request.user.id
        
        repo = SinhVienRepository()
        use_case = GetSinhVienInfoUseCase(repo)
        
        result = use_case.execute(str(user_id))
        
        http_status = result.status_code or 200
        
        return Response(result.to_dict(), status=http_status)
