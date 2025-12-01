"""
Presentation Layer - GV (Giang Vien) API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

from application.gv.use_cases import (
    GetGVLopHocPhanListUseCase,
    GetGVLopHocPhanDetailUseCase,
    GetGVStudentsOfLHPUseCase,
    GetGVGradesUseCase,
    UpsertGVGradesUseCase,
    GetGVTKBWeeklyUseCase,
)
from infrastructure.persistence.gv.gv_lop_hoc_phan_repository import GVLopHocPhanRepository
from infrastructure.persistence.gv.gv_grade_repository import GVGradeRepository
from infrastructure.persistence.gv.gv_tkb_repository import GVTKBRepository


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
        grades = request.data.get('diem', [])
        
        lhp_repo = GVLopHocPhanRepository()
        grade_repo = GVGradeRepository()
        use_case = UpsertGVGradesUseCase(lhp_repo, grade_repo)
        
        result = use_case.execute(lhp_id, user_id, grades)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GVTKBWeeklyView(APIView):
    """
    Get weekly timetable for GV
    GET /api/gv/tkb-weekly?hocKyId=...&dateStart=YYYY-MM-DD&dateEnd=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = str(request.user.id)
        hoc_ky_id = request.query_params.get('hocKyId')
        date_start_str = request.query_params.get('dateStart')
        date_end_str = request.query_params.get('dateEnd')
        
        # Validate required params
        if not hoc_ky_id:
            return Response({
                'isSuccess': False,
                'message': 'hocKyId is required',
                'data': None
            }, status=400)
        
        if not date_start_str or not date_end_str:
            return Response({
                'isSuccess': False,
                'message': 'dateStart and dateEnd are required',
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
