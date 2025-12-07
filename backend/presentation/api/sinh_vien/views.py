"""
Presentation Layer - SinhVien API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from application.sinh_vien.use_cases import GetSinhVienInfoUseCase
from application.tai_lieu.use_cases import (
    GetSVTaiLieuUseCase,
    DownloadSVTaiLieuUseCase,
)
from infrastructure.persistence.sinh_vien import SinhVienRepository
from infrastructure.persistence.tai_lieu.repository import TaiLieuRepository
from infrastructure.persistence.s3_service import get_s3_service


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


# ============ TAI LIEU (Documents) ============

class SVTaiLieuListView(APIView):
    """
    Get list of TaiLieu for a LopHocPhan
    GET /api/sv/lop-hoc-phan/<id>/tai-lieu
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lhp_id):
        user_id = str(request.user.id)
        
        repo = TaiLieuRepository()
        use_case = GetSVTaiLieuUseCase(repo)
        
        result = use_case.execute(lhp_id, user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class SVTaiLieuDownloadView(APIView):
    """
    Download TaiLieu (stream file from S3)
    GET /api/sv/lop-hoc-phan/<lhp_id>/tai-lieu/<doc_id>/download
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lhp_id, doc_id):
        user_id = str(request.user.id)
        
        repo = TaiLieuRepository()
        s3_service = get_s3_service()
        use_case = DownloadSVTaiLieuUseCase(repo, s3_service)
        
        result = use_case.execute(lhp_id, doc_id, user_id)
        
        if not result.success:
            return Response(result.to_dict(), status=result.status_code or 400)
        
        # Stream file to response
        file_data = result.data
        response = HttpResponse(
            file_data['content'],
            content_type=file_data['content_type']
        )
        
        # Set filename for download
        filename = file_data['filename']
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
