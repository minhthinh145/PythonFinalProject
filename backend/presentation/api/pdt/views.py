from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.set_hoc_ky_hien_hanh_use_case import SetHocKyHienHanhUseCase
from application.pdt.use_cases.create_bulk_ky_phase_use_case import CreateBulkKyPhaseUseCase
from infrastructure.persistence.enrollment.repositories import KyPhaseRepository, DotDangKyRepository
from infrastructure.persistence.common.repositories import HocKyRepository

class SetHocKyHienHanhView(APIView):
    """
    POST /api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh
    """
    permission_classes = [IsAuthenticated] # TODO: Add Role Check

    def post(self, request):
        hoc_ky_id = request.data.get('hocKyId')
        
        use_case = SetHocKyHienHanhUseCase(HocKyRepository())
        result = use_case.execute(hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class CreateBulkKyPhaseView(APIView):
    """
    POST /api/pdt/quan-ly-hoc-ky/ky-phase/bulk
    """
    permission_classes = [IsAuthenticated] # TODO: Add Role Check

    def post(self, request):
        data = request.data
        
        use_case = CreateBulkKyPhaseUseCase(
            ky_phase_repo=KyPhaseRepository(),
            hoc_ky_repo=HocKyRepository(),
            dot_dang_ky_repo=DotDangKyRepository()
        )
        result = use_case.execute(data)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetPhasesByHocKyView(APIView):
    """
    GET /api/pdt/quan-ly-hoc-ky/ky-phase/{hocKyId}
    """
    permission_classes = [IsAuthenticated] # TODO: Add Role Check

    def get(self, request, hocKyId):
        from application.pdt.use_cases.get_phases_by_hoc_ky_use_case import GetPhasesByHocKyUseCase
        
        use_case = GetPhasesByHocKyUseCase(KyPhaseRepository())
        result = use_case.execute(hocKyId)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class UpdateDotGhiDanhView(APIView):
    """
    POST /api/pdt/dot-ghi-danh/update
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from application.pdt.use_cases.registration_period_use_cases import UpdateDotGhiDanhUseCase
        
        use_case = UpdateDotGhiDanhUseCase(DotDangKyRepository())
        result = use_case.execute(request.data)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetDotGhiDanhByHocKyView(APIView):
    """
    GET /api/pdt/dot-dang-ky/{hocKyId}
    Note: FE maps this to getDotGhiDanhByHocKy, likely expecting 'ghi_danh' type
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, hocKyId):
        from application.pdt.use_cases.registration_period_use_cases import GetDotGhiDanhByHocKyUseCase
        
        use_case = GetDotGhiDanhByHocKyUseCase(DotDangKyRepository())
        result = use_case.execute(hocKyId)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class DotDangKyView(APIView):
    """
    GET /api/pdt/dot-dang-ky?hoc_ky_id=...
    PUT /api/pdt/dot-dang-ky
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoc_ky_id = request.query_params.get('hoc_ky_id')
        if not hoc_ky_id:
            return Response({"success": False, "message": "Missing hoc_ky_id"}, status=400)
            
        from application.pdt.use_cases.registration_period_use_cases import GetDotDangKyByHocKyUseCase
        
        use_case = GetDotDangKyByHocKyUseCase(DotDangKyRepository())
        result = use_case.execute(hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)

    def put(self, request):
        from application.pdt.use_cases.registration_period_use_cases import UpdateDotDangKyUseCase
        
        use_case = UpdateDotDangKyUseCase(DotDangKyRepository())
        result = use_case.execute(request.data)
        
        return Response(result.to_dict(), status=result.status_code or 200)

class GetDanhSachKhoaView(APIView):
    """
    GET /api/pdt/khoa
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from application.pdt.use_cases.get_danh_sach_khoa_use_case import GetDanhSachKhoaUseCase
        from infrastructure.persistence.enrollment.repositories import KhoaRepository
        
        use_case = GetDanhSachKhoaUseCase(KhoaRepository())
        result = use_case.execute()
        
        return Response(result, status=200)


class UpdateHocKyDatesView(APIView):
    """
    PATCH /api/hoc-ky/dates
    Body: { hocKyId, ngayBatDau, ngayKetThuc }
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        import logging
        import json
        logger = logging.getLogger(__name__)
        
        data = request.data
        logger.info(f"UpdateHocKyDates raw request.data: {data}")
        
        # Handle case where JSON is sent as form-urlencoded (key is JSON string)
        if isinstance(data, dict) and len(data) == 1:
            first_key = list(data.keys())[0]
            if first_key.startswith('{') and first_key.endswith('}'):
                try:
                    data = json.loads(first_key)
                    logger.info(f"Parsed JSON from key: {data}")
                except json.JSONDecodeError:
                    pass
        
        # Support both camelCase and snake_case
        hoc_ky_id = data.get('hocKyId') or data.get('hoc_ky_id')
        ngay_bat_dau = data.get('ngayBatDau') or data.get('ngay_bat_dau')
        ngay_ket_thuc = data.get('ngayKetThuc') or data.get('ngay_ket_thuc')
        
        logger.info(f"Parsed: hoc_ky_id={hoc_ky_id}, ngay_bat_dau={ngay_bat_dau}, ngay_ket_thuc={ngay_ket_thuc}")
        
        if not hoc_ky_id:
            return Response({
                "isSuccess": False,
                "message": f"Thiếu hocKyId",
                "errorCode": "MISSING_PARAM"
            }, status=400)
        
        try:
            from infrastructure.persistence.models import HocKy
            from django.utils import timezone
            
            hoc_ky = HocKy.objects.using('neon').filter(id=hoc_ky_id).first()
            
            if not hoc_ky:
                return Response({
                    "isSuccess": False,
                    "message": "Không tìm thấy học kỳ",
                    "errorCode": "NOT_FOUND"
                }, status=404)
            
            # Update dates if provided
            if ngay_bat_dau:
                hoc_ky.ngay_bat_dau = ngay_bat_dau
            if ngay_ket_thuc:
                hoc_ky.ngay_ket_thuc = ngay_ket_thuc
            
            hoc_ky.updated_at = timezone.now()
            hoc_ky.save(using='neon')
            
            return Response({
                "isSuccess": True,
                "message": "Cập nhật ngày học kỳ thành công",
                "data": {
                    "id": str(hoc_ky.id),
                    "tenHocKy": hoc_ky.ten_hoc_ky,
                    "ngayBatDau": str(hoc_ky.ngay_bat_dau) if hoc_ky.ngay_bat_dau else None,
                    "ngayKetThuc": str(hoc_ky.ngay_ket_thuc) if hoc_ky.ngay_ket_thuc else None
                }
            }, status=200)
            
        except Exception as e:
            return Response({
                "isSuccess": False,
                "message": f"Lỗi: {str(e)}",
                "errorCode": "INTERNAL_ERROR"
            }, status=500)
