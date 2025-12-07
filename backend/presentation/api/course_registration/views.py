"""
Presentation Layer - Course Registration API Views
"""
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from application.course_registration.use_cases.check_phase_dang_ky_use_case import CheckPhaseDangKyUseCase
from application.course_registration.use_cases.get_danh_sach_lop_hoc_phan_use_case import GetDanhSachLopHocPhanUseCase
from application.course_registration.use_cases.get_danh_sach_lop_da_dang_ky_use_case import GetDanhSachLopDaDangKyUseCase
from application.course_registration.use_cases.dang_ky_hoc_phan_use_case import DangKyHocPhanUseCase
from application.course_registration.use_cases.huy_dang_ky_hoc_phan_use_case import HuyDangKyHocPhanUseCase
from application.course_registration.use_cases.chuyen_lop_hoc_phan_use_case import ChuyenLopHocPhanUseCase
from application.course_registration.use_cases.chuyen_lop_hoc_phan_use_case import ChuyenLopHocPhanUseCase
from application.course_registration.use_cases.get_lop_chua_dang_ky_by_mon_hoc_use_case import GetLopChuaDangKyByMonHocUseCase
from application.course_registration.use_cases.get_lich_su_dang_ky_use_case import GetLichSuDangKyUseCase
from application.course_registration.use_cases.get_tkb_weekly_use_case import GetTKBWeeklyUseCase
from infrastructure.persistence.enrollment.repositories import KyPhaseRepository
from infrastructure.persistence.sinh_vien.sinh_vien_repository import SinhVienRepository
from infrastructure.persistence.course_registration.repositories import (
    LopHocPhanRepository, 
    DangKyHocPhanRepository,
    DangKyTKBRepository,
    LichSuDangKyRepository
)

class CheckPhaseDangKyView(APIView):
    """
    GET /api/sv/check-phase-dang-ky
    
    Check if course registration phase is active
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Accept both hocKyId (camelCase) and hoc_ky_id (snake_case)
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu học kỳ ID",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        repo = KyPhaseRepository()
        use_case = CheckPhaseDangKyUseCase(repo)
        
        result = use_case.execute(hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetDanhSachLopHocPhanView(APIView):
    """
    GET /api/sv/lop-hoc-phan
    
    Get list of available course classes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Accept both hocKyId (camelCase) and hoc_ky_id (snake_case)
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu học kỳ ID",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        lhp_repo = LopHocPhanRepository()
        dkhp_repo = DangKyHocPhanRepository()
        use_case = GetDanhSachLopHocPhanUseCase(lhp_repo, dkhp_repo)
        
        result = use_case.execute(str(request.user.id), hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetDanhSachLopDaDangKyView(APIView):
    """
    GET /api/sv/lop-da-dang-ky
    
    Get list of registered course classes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Accept both hocKyId (camelCase) and hoc_ky_id (snake_case)
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu học kỳ ID",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        dkhp_repo = DangKyHocPhanRepository()
        use_case = GetDanhSachLopDaDangKyUseCase(dkhp_repo)
        
        result = use_case.execute(str(request.user.id), hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class DangKyLopHocPhanView(APIView):
    """
    POST /api/sv/dang-ky-hoc-phan
    
    Register for a course class
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        lop_hoc_phan_id = request.data.get('lopHocPhanId')
        hoc_ky_id = request.data.get('hocKyId')
        
        if not lop_hoc_phan_id or not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin đăng ký (lopHocPhanId, hocKyId)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        use_case = DangKyHocPhanUseCase(
            LopHocPhanRepository(),
            DangKyHocPhanRepository(),
            DangKyTKBRepository(),
            LichSuDangKyRepository(),
            KyPhaseRepository(),
            SinhVienRepository()
        )
        
        result = use_case.execute(str(request.user.id), lop_hoc_phan_id, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class HuyDangKyLopHocPhanView(APIView):
    """
    POST /api/sv/huy-dang-ky-hoc-phan
    
    Cancel course registration
    Body: {"lop_hoc_phan_id": "uuid"} or {"lopHocPhanId": "uuid"}
    hoc_ky_id is optional - will use hoc_ky_hien_hanh if not provided
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Accept both snake_case and camelCase
        lop_hoc_phan_id = request.data.get('lop_hoc_phan_id') or request.data.get('lopHocPhanId')
        hoc_ky_id = request.data.get('hoc_ky_id') or request.data.get('hocKyId')  # Optional
        
        if not lop_hoc_phan_id:
            return Response({
                "success": False,
                "message": "Thiếu lop_hoc_phan_id hoặc lopHocPhanId",
                "errorCode": "MISSING_LOP_HOC_PHAN_ID"
            }, status=400)
            
        use_case = HuyDangKyHocPhanUseCase(
            LopHocPhanRepository(),
            DangKyHocPhanRepository(),
            DangKyTKBRepository(),
            LichSuDangKyRepository(),
            KyPhaseRepository(),
            SinhVienRepository()
        )
        
        # hoc_ky_id is optional - use case will get hoc_ky_hien_hanh if not provided
        result = use_case.execute(str(request.user.id), lop_hoc_phan_id, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class ChuyenLopHocPhanView(APIView):
    """
    POST /api/sv/chuyen-lop-hoc-phan
    
    Transfer course class
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Accept both camelCase and snake_case
        lop_cu_id = request.data.get('lop_hoc_phan_id_cu') or request.data.get('lopCuId') or request.data.get('lop_cu_id')
        lop_moi_id = request.data.get('lop_hoc_phan_id_moi') or request.data.get('lopMoiId') or request.data.get('lop_moi_id')
        hoc_ky_id = request.data.get('hoc_ky_id') or request.data.get('hocKyId')
        
        if not lop_cu_id or not lop_moi_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin chuyển lớp (lop_hoc_phan_id_cu, lop_hoc_phan_id_moi)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        use_case = ChuyenLopHocPhanUseCase(
            LopHocPhanRepository(),
            DangKyHocPhanRepository(),
            DangKyTKBRepository(),
            LichSuDangKyRepository(),
            KyPhaseRepository(),
            SinhVienRepository()
        )
        
        # hoc_ky_id is optional - use case will get hoc_ky_hien_hanh if not provided
        result = use_case.execute(str(request.user.id), lop_cu_id, lop_moi_id, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetLopChuaDangKyByMonHocView(APIView):
    """
    GET /api/sv/lop-hoc-phan/mon-hoc
    
    Get list of classes for a subject that student hasn't registered for (for switching)
    Accepts mon_hoc_id as either ma_mon (e.g., 'COMP1325') or UUID
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Accept monHocId/mon_hoc_id - can be ma_mon (string) or UUID
        mon_hoc_id = request.query_params.get('monHocId') or request.query_params.get('mon_hoc_id')
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not mon_hoc_id or not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin (monHocId/mon_hoc_id, hocKyId/hoc_ky_id)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        use_case = GetLopChuaDangKyByMonHocUseCase(
            LopHocPhanRepository(),
            DangKyHocPhanRepository()
        )
        
        result = use_case.execute(str(request.user.id), mon_hoc_id, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetLichSuDangKyView(APIView):
    """
    GET /api/sv/lich-su-dang-ky
    
    Get registration history
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin (hocKyId)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        use_case = GetLichSuDangKyUseCase(LichSuDangKyRepository())
        
        result = use_case.execute(str(request.user.id), hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetTKBWeeklyView(APIView):
    """
    GET /api/sv/tkb-weekly
    
    Get weekly schedule
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        date_start_str = request.query_params.get('dateStart') or request.query_params.get('date_start')
        date_end_str = request.query_params.get('dateEnd') or request.query_params.get('date_end')
        
        logger.info(f"🔍 TKB Weekly: user_id={request.user.id}, hoc_ky_id={hoc_ky_id}, dates={date_start_str} to {date_end_str}")
        
        if not hoc_ky_id or not date_start_str or not date_end_str:
            return Response({
                "success": False,
                "message": "Thiếu thông tin (hocKyId, dateStart, dateEnd)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        try:
            date_start = datetime.strptime(date_start_str, '%Y-%m-%d').date()
            date_end = datetime.strptime(date_end_str, '%Y-%m-%d').date()
        except ValueError:
             return Response({
                "success": False,
                "message": "Ngày không hợp lệ (YYYY-MM-DD)",
                "errorCode": "INVALID_DATE"
            }, status=400)

        # Get sinh_vien_id from user
        # request.user is UserWrapper, need to extract the actual UUID string
        # SinhVien.id is OneToOne to Users.id
        from infrastructure.persistence.models import SinhVien
        user_id = str(request.user)  # UserWrapper.__str__ returns str(self._user.id)
        sinh_vien = SinhVien.objects.using('neon').filter(
            id=user_id
        ).first()
        
        logger.info(f"🔍 SinhVien lookup: user_id={request.user.id} -> sinh_vien={sinh_vien.id_id if sinh_vien else 'NOT FOUND'}")
        
        if not sinh_vien:
            return Response({
                "isSuccess": False,
                "message": "Không tìm thấy thông tin sinh viên",
                "data": [],
                "errorCode": "NOT_FOUND"
            }, status=200)

        use_case = GetTKBWeeklyUseCase(DangKyHocPhanRepository())
        
        result = use_case.execute(str(sinh_vien.pk), hoc_ky_id, date_start, date_end)
        
        logger.info(f"🔍 TKB Result: success={result.success}, data_count={len(result.data) if result.data else 0}")
        
        return Response(result.to_dict(), status=result.status_code or 200)

class TraCuuHocPhanView(APIView):
    """
    GET /api/sv/tra-cuu-hoc-phan
    
    Lookup open subjects for a semester
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin (hocKyId)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        from application.course_registration.use_cases.tra_cuu_hoc_phan_use_case import TraCuuHocPhanUseCase
        from infrastructure.persistence.enrollment.repositories import HocPhanRepository
        
        use_case = TraCuuHocPhanUseCase(HocPhanRepository())
        
        result = use_case.execute(hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetChiTietHocPhiView(APIView):
    """
    GET /api/sv/hoc-phi
    
    Get tuition details for a semester
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin (hocKyId)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
            
        from application.course_registration.use_cases.get_chi_tiet_hoc_phi_use_case import GetChiTietHocPhiUseCase
        from infrastructure.persistence.course_registration.repositories import HocPhiRepository
        
        use_case = GetChiTietHocPhiUseCase(HocPhiRepository())
        
        result = use_case.execute(str(request.user.id), hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GetTaiLieuByLopHocPhanView(APIView):
    """
    GET /api/sv/lop-hoc-phan/{id}/tai-lieu
    
    Get documents for a specific class
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, lop_hoc_phan_id):
        from application.course_registration.use_cases.get_tai_lieu_use_case import GetTaiLieuByLopHocPhanUseCase
        from infrastructure.persistence.course_registration.repositories import TaiLieuRepository, DangKyHocPhanRepository
        
        use_case = GetTaiLieuByLopHocPhanUseCase(TaiLieuRepository(), DangKyHocPhanRepository())
        
        result = use_case.execute(str(request.user.id), lop_hoc_phan_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GetLopDaDangKyWithTaiLieuView(APIView):
    """
    GET /api/sv/lop-da-dang-ky/tai-lieu
    
    Get registered classes with their documents
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        hoc_ky_id = request.query_params.get('hocKyId') or request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin (hocKyId)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
        
        from application.course_registration.use_cases.get_tai_lieu_use_case import GetLopDaDangKyWithTaiLieuUseCase
        from infrastructure.persistence.course_registration.repositories import TaiLieuRepository, DangKyHocPhanRepository
        
        use_case = GetLopDaDangKyWithTaiLieuUseCase(DangKyHocPhanRepository(), TaiLieuRepository())
        
        result = use_case.execute(str(request.user.id), hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)
