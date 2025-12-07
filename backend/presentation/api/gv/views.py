"""
Presentation Layer - GV (Giang Vien) API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from datetime import datetime

from application.gv.use_cases import (
    GetGVLopHocPhanListUseCase,
    GetGVLopHocPhanDetailUseCase,
    GetGVStudentsOfLHPUseCase,
    GetGVGradesUseCase,
    UpsertGVGradesUseCase,
    GetGVTKBWeeklyUseCase,
)
from application.tai_lieu.use_cases import (
    GetTaiLieuByLHPUseCase,
    UploadTaiLieuUseCase,
    DeleteTaiLieuUseCase,
    UpdateTaiLieuUseCase,
    DownloadTaiLieuUseCase,
)
from infrastructure.persistence.gv.gv_lop_hoc_phan_repository import GVLopHocPhanRepository
from infrastructure.persistence.gv.gv_grade_repository import GVGradeRepository
from infrastructure.persistence.gv.gv_tkb_repository import GVTKBRepository
from infrastructure.persistence.tai_lieu.repository import TaiLieuRepository
from infrastructure.persistence.s3_service import get_s3_service


class GVLopHocPhanListView(APIView):
    """
    Get list of LopHocPhan assigned to GV
    GET /api/gv/lop-hoc-phan?hocKyId=...
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = str(request.user.id)
        hoc_ky_id = request.query_params.get('hocKyId')
        
        repo = GVLopHocPhanRepository()
        use_case = GetGVLopHocPhanListUseCase(repo)
        
        result = use_case.execute(user_id, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GVLopHocPhanDetailView(APIView):
    """
    Get detail of a LopHocPhan
    GET /api/gv/lop-hoc-phan/<id>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lhp_id):
        user_id = str(request.user.id)
        
        repo = GVLopHocPhanRepository()
        use_case = GetGVLopHocPhanDetailUseCase(repo)
        
        result = use_case.execute(lhp_id, user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GVLopHocPhanStudentsView(APIView):
    """
    Get students of a LopHocPhan
    GET /api/gv/lop-hoc-phan/<id>/sinh-vien
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lhp_id):
        user_id = str(request.user.id)
        
        repo = GVLopHocPhanRepository()
        use_case = GetGVStudentsOfLHPUseCase(repo)
        
        result = use_case.execute(lhp_id, user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GVLopHocPhanGradesView(APIView):
    """
    Get/Update grades of a LopHocPhan
    GET /api/gv/lop-hoc-phan/<id>/diem
    PUT /api/gv/lop-hoc-phan/<id>/diem
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lhp_id):
        user_id = str(request.user.id)
        
        lhp_repo = GVLopHocPhanRepository()
        grade_repo = GVGradeRepository()
        use_case = GetGVGradesUseCase(lhp_repo, grade_repo)
        
        result = use_case.execute(lhp_id, user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)
    
    def put(self, request, lhp_id):
        user_id = str(request.user.id)
        # Accept both 'items' (FE sends this) and 'diem' (legacy)
        grades = request.data.get('items') or request.data.get('diem', [])
        
        lhp_repo = GVLopHocPhanRepository()
        grade_repo = GVGradeRepository()
        use_case = UpsertGVGradesUseCase(lhp_repo, grade_repo)
        
        result = use_case.execute(lhp_id, user_id, grades)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GVTKBWeeklyView(APIView):
    """
    Get weekly timetable for GV
    GET /api/gv/tkb-weekly?hoc_ky_id=...&date_start=YYYY-MM-DD&date_end=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = str(request.user.id)
        # Accept both snake_case and camelCase for compatibility
        hoc_ky_id = request.query_params.get('hoc_ky_id') or request.query_params.get('hocKyId')
        date_start_str = request.query_params.get('date_start') or request.query_params.get('dateStart')
        date_end_str = request.query_params.get('date_end') or request.query_params.get('dateEnd')
        
        # Validate required params
        if not hoc_ky_id:
            return Response({
                'isSuccess': False,
                'message': 'hoc_ky_id is required',
                'data': None
            }, status=400)
        
        if not date_start_str or not date_end_str:
            return Response({
                'isSuccess': False,
                'message': 'date_start and date_end are required',
                'data': None
            }, status=400)
        
        # Parse dates
        try:
            date_start = datetime.strptime(date_start_str, '%Y-%m-%d').date()
            date_end = datetime.strptime(date_end_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'isSuccess': False,
                'message': 'Invalid date format. Use YYYY-MM-DD',
                'data': None
            }, status=400)
        
        repo = GVTKBRepository()
        use_case = GetGVTKBWeeklyUseCase(repo)
        
        result = use_case.execute(user_id, hoc_ky_id, date_start, date_end)
        
        return Response(result.to_dict(), status=result.status_code or 200)


# ============ TAI LIEU (Documents) ============

class GVTaiLieuListView(APIView):
    """
    Get list of TaiLieu for a LopHocPhan
    GET /api/gv/lop-hoc-phan/<id>/tai-lieu
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lhp_id):
        user_id = str(request.user.id)
        
        repo = TaiLieuRepository()
        use_case = GetTaiLieuByLHPUseCase(repo)
        
        result = use_case.execute(lhp_id, user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GVTaiLieuUploadView(APIView):
    """
    Upload TaiLieu for a LopHocPhan
    POST /api/gv/lop-hoc-phan/<id>/tai-lieu/upload
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, lhp_id):
        user_id = str(request.user.id)
        
        # Get file from request
        file = request.FILES.get('file')
        if not file:
            return Response({
                'isSuccess': False,
                'message': 'Không có file được upload',
                'data': None
            }, status=400)
        
        ten_tai_lieu = request.data.get('ten_tai_lieu', file.name)
        
        repo = TaiLieuRepository()
        s3_service = get_s3_service()
        use_case = UploadTaiLieuUseCase(repo, s3_service)
        
        result = use_case.execute(
            lhp_id=lhp_id,
            gv_user_id=user_id,
            file_obj=file,
            filename=file.name,
            content_type=file.content_type or 'application/octet-stream',
            file_size=file.size,
            ten_tai_lieu=ten_tai_lieu
        )
        
        status_code = 201 if result.success else (result.status_code or 400)
        return Response(result.to_dict(), status=status_code)


class GVTaiLieuDetailView(APIView):
    """
    Delete or Update TaiLieu
    DELETE /api/gv/lop-hoc-phan/<lhp_id>/tai-lieu/<doc_id>
    PUT /api/gv/lop-hoc-phan/<lhp_id>/tai-lieu/<doc_id>
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, lhp_id, doc_id):
        user_id = str(request.user.id)
        
        repo = TaiLieuRepository()
        s3_service = get_s3_service()
        use_case = DeleteTaiLieuUseCase(repo, s3_service)
        
        result = use_case.execute(lhp_id, doc_id, user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)
    
    def put(self, request, lhp_id, doc_id):
        user_id = str(request.user.id)
        new_name = request.data.get('ten_tai_lieu', '')
        
        if not new_name:
            return Response({
                'isSuccess': False,
                'message': 'Thiếu tên tài liệu',
                'data': None
            }, status=400)
        
        repo = TaiLieuRepository()
        use_case = UpdateTaiLieuUseCase(repo)
        
        result = use_case.execute(lhp_id, doc_id, user_id, new_name)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GVTaiLieuDownloadView(APIView):
    """
    Download TaiLieu (stream file from S3)
    GET /api/gv/lop-hoc-phan/<lhp_id>/tai-lieu/<doc_id>/download
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lhp_id, doc_id):
        user_id = str(request.user.id)
        
        repo = TaiLieuRepository()
        s3_service = get_s3_service()
        use_case = DownloadTaiLieuUseCase(repo, s3_service)
        
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
