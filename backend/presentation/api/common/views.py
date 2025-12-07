"""
Presentation Layer - Common Public API Views

Views for common/shared endpoints used by all roles
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from application.common.use_cases.get_hoc_ky_hien_hanh_use_case import GetHocKyHienHanhUseCase
from application.enrollment.use_cases import GetHocKyUseCase
from infrastructure.persistence.common.repositories import HocKyRepository, NienKhoaRepository, NganhRepository
from infrastructure.persistence.enrollment.repositories import HocKyRepository as EnrollmentHocKyRepo


class GetHocKyHienHanhView(APIView):
    """
    GET /api/hoc-ky-hien-hanh
    
    Get the current active semester
    Requires authentication
    All roles can access
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        hoc_ky_repo = HocKyRepository()
        nien_khoa_repo = NienKhoaRepository()
        use_case = GetHocKyHienHanhUseCase(hoc_ky_repo, nien_khoa_repo)
        
        result = use_case.execute()
        
        # Return 404 if not found, 200 otherwise
        status_code = 404 if (result.success and result.data is None) else (result.status_code or 200)
        
        return Response(result.to_dict(), status=status_code)


class GetHocKyNienKhoaView(APIView):
    """
    GET /api/hoc-ky-nien-khoa
    
    Get all semesters with academic years
    Requires authentication
    All roles can access
    
    Note: This already exists, but keeping for reference
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        hoc_ky_repo = EnrollmentHocKyRepo()
        use_case = GetHocKyUseCase(hoc_ky_repo)
        
        result = use_case.execute()
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GetDanhSachNganhView(APIView):
    """
    GET /api/dm/nganh?khoa_id={id}
    
    Get list of programs/majors
    Optional filter by faculty (khoa_id)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        khoa_id = request.query_params.get('khoa_id')
        
        nganh_repo = NganhRepository()
        nganh_list = nganh_repo.find_all(khoa_id)
        
        data = [{
            'id': str(n.id),
            'tenNganh': n.ten_nganh,
            'maNganh': n.ma_nganh,
            'khoaId': str(n.khoa_id) if n.khoa_id else None,
            'tenKhoa': n.khoa.ten_khoa if n.khoa else None
        } for n in nganh_list]
        
        from core.types import ServiceResult
        result = ServiceResult.ok(data, f"Lấy thành công {len(data)} ngành")
        
        return Response(result.to_dict(), status=200)


class GetDanhSachKhoaView(APIView):
    """
    GET /api/dm/khoa
    
    Get list of faculties/departments
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from infrastructure.persistence.models import Khoa
        from core.types import ServiceResult
        
        try:
            khoas = Khoa.objects.using('neon').all().order_by('ten_khoa')
            
            data = [{
                'id': str(k.id),
                'tenKhoa': k.ten_khoa,
                'maKhoa': k.ma_khoa if hasattr(k, 'ma_khoa') else None
            } for k in khoas]
            
            result = ServiceResult.ok(data, f"Lấy thành công {len(data)} khoa")
            return Response(result.to_dict(), status=200)
        except Exception as e:
            result = ServiceResult.fail(str(e))
            return Response(result.to_dict(), status=500)


class GetNganhChuaCoChinhSachView(APIView):
    """
    GET /api/dm/nganh/chua-co-chinh-sach?hoc_ky_id={}&khoa_id={}
    
    Get list of majors/programs that don't have credit policy for the given semester
    Used in the form to add new credit policies
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from infrastructure.persistence.models import NganhHoc, ChinhSachTinChi
        from core.types import ServiceResult
        
        hoc_ky_id = request.query_params.get('hoc_ky_id')
        khoa_id = request.query_params.get('khoa_id')
        
        if not hoc_ky_id:
            result = ServiceResult.fail("Thiếu học kỳ ID")
            return Response(result.to_dict(), status=400)
        
        if not khoa_id:
            result = ServiceResult.fail("Thiếu khoa ID")
            return Response(result.to_dict(), status=400)
        
        try:
            # Get list of nganh_ids that already have policy in this hoc_ky
            existing_policy_nganh_ids = ChinhSachTinChi.objects.using('neon').filter(
                hoc_ky_id=hoc_ky_id
            ).values_list('nganh_id', flat=True)
            
            # Get ngành thuộc khoa mà KHÔNG có chính sách trong học kỳ này
            nganh_list = NganhHoc.objects.using('neon').filter(
                khoa_id=khoa_id
            ).exclude(
                id__in=existing_policy_nganh_ids
            ).order_by('ten_nganh')
            
            data = [{
                'id': str(n.id),
                'ma_nganh': n.ma_nganh,
                'ten_nganh': n.ten_nganh,
                'khoa_id': str(n.khoa_id) if n.khoa_id else None
            } for n in nganh_list]
            
            result = ServiceResult.ok(data, f"Lấy thành công {len(data)} ngành chưa có chính sách")
            return Response(result.to_dict(), status=200)
        except Exception as e:
            result = ServiceResult.fail(str(e))
            return Response(result.to_dict(), status=500)
