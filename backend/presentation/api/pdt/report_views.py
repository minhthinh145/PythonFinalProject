from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.report_use_cases import (
    GetOverviewStatsUseCase, GetKhoaStatsUseCase, 
    GetNganhStatsUseCase, GetGiangVienStatsUseCase
)
from django.http import HttpResponse

class OverviewStatsView(APIView):
    """
    GET /api/pdt/bao-cao/overview
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoc_ky_id = request.query_params.get('hoc_ky_id')
        khoa_id = request.query_params.get('khoa_id')
        nganh_id = request.query_params.get('nganh_id')

        if not hoc_ky_id:
            return Response({"isSuccess": False, "message": "hoc_ky_id is required"}, status=400)

        use_case = GetOverviewStatsUseCase()
        result = use_case.execute(hoc_ky_id, khoa_id, nganh_id)
        return Response(result.to_dict(), status=result.status_code or 200)

class KhoaStatsView(APIView):
    """
    GET /api/pdt/bao-cao/dk-theo-khoa
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoc_ky_id = request.query_params.get('hoc_ky_id')
        
        if not hoc_ky_id:
            return Response({"isSuccess": False, "message": "hoc_ky_id is required"}, status=400)

        use_case = GetKhoaStatsUseCase()
        result = use_case.execute(hoc_ky_id)
        return Response(result.to_dict(), status=result.status_code or 200)

class NganhStatsView(APIView):
    """
    GET /api/pdt/bao-cao/dk-theo-nganh
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoc_ky_id = request.query_params.get('hoc_ky_id')
        khoa_id = request.query_params.get('khoa_id')
        
        if not hoc_ky_id:
            return Response({"isSuccess": False, "message": "hoc_ky_id is required"}, status=400)

        use_case = GetNganhStatsUseCase()
        result = use_case.execute(hoc_ky_id, khoa_id)
        return Response(result.to_dict(), status=result.status_code or 200)

class GiangVienStatsView(APIView):
    """
    GET /api/pdt/bao-cao/tai-giang-vien
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoc_ky_id = request.query_params.get('hoc_ky_id')
        khoa_id = request.query_params.get('khoa_id')
        
        if not hoc_ky_id:
            return Response({"isSuccess": False, "message": "hoc_ky_id is required"}, status=400)

        use_case = GetGiangVienStatsUseCase()
        result = use_case.execute(hoc_ky_id, khoa_id)
        return Response(result.to_dict(), status=result.status_code or 200)

class ExportExcelView(APIView):
    """
    GET /api/pdt/bao-cao/export/excel
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Placeholder for Excel export
        # In a real implementation, this would generate an .xlsx file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
        # Write dummy content or implement actual export logic
        return response

class ExportPDFView(APIView):
    """
    POST /api/pdt/bao-cao/export/pdf
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Placeholder for PDF export
        # In a real implementation, this would take chart images and generate a PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        return response
