"""
Presentation Layer - Enrollment API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from application.enrollment.use_cases import (
    CheckGhiDanhUseCase,
    GetMonHocGhiDanhUseCase,
    GhiDanhMonHocUseCase,
    GetDanhSachDaGhiDanhUseCase
)
from infrastructure.persistence.enrollment import (
    HocKyRepository,
    KyPhaseRepository,
    DotDangKyRepository,
    HocPhanRepository,
    GhiDanhRepository
)
from infrastructure.persistence.sinh_vien import SinhVienRepository

class EnrollmentBaseView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_repositories(self):
        return {
            'hoc_ky': HocKyRepository(),
            'ky_phase': KyPhaseRepository(),
            'dot_dang_ky': DotDangKyRepository(),
            'sinh_vien': SinhVienRepository(),
            'hoc_phan': HocPhanRepository(),
            'ghi_danh': GhiDanhRepository()
        }

class CheckGhiDanhStatusView(EnrollmentBaseView):
    """
    GET /api/sv/ghi-danh/check-status
    """
    def get(self, request):
        repos = self.get_repositories()
        use_case = CheckGhiDanhUseCase(
            repos['hoc_ky'],
            repos['ky_phase'],
            repos['dot_dang_ky'],
            repos['sinh_vien']
        )
        
        result = use_case.execute(str(request.user.id))
        
        return Response({
            'isSuccess': result.success,
            'message': result.message,
            'data': result.data,
            'errorCode': result.error_code
        }, status=result.status_code or 200)

class GetMonHocGhiDanhView(EnrollmentBaseView):
    """
    GET /api/sv/ghi-danh/mon-hoc
    """
    def get(self, request):
        hoc_ky_id = request.query_params.get('hocKyId')
        repos = self.get_repositories()
        use_case = GetMonHocGhiDanhUseCase(
            repos['hoc_ky'],
            repos['hoc_phan']
        )
        
        result = use_case.execute(hoc_ky_id)
        
        return Response({
            'isSuccess': result.success,
            'message': result.message,
            'data': result.data,
            'errorCode': result.error_code
        }, status=result.status_code or 200)

class GhiDanhMonHocView(EnrollmentBaseView):
    """
    POST /api/sv/ghi-danh/dang-ky
    """
    def post(self, request):
        repos = self.get_repositories()
        use_case = GhiDanhMonHocUseCase(
            repos['hoc_phan'],
            repos['ghi_danh']
        )
        
        result = use_case.execute(request.data, str(request.user.id))
        
        return Response({
            'isSuccess': result.success,
            'message': result.message,
            'data': result.data,
            'errorCode': result.error_code
        }, status=result.status_code or 200)

class GetDanhSachDaGhiDanhView(EnrollmentBaseView):
    """
    GET /api/sv/ghi-danh/da-ghi-danh
    """
    def get(self, request):
        repos = self.get_repositories()
        use_case = GetDanhSachDaGhiDanhUseCase(repos['ghi_danh'])
        
        result = use_case.execute(str(request.user.id))
        
        return Response({
            'isSuccess': result.success,
            'message': result.message,
            'data': result.data,
            'errorCode': result.error_code
        }, status=result.status_code or 200)
