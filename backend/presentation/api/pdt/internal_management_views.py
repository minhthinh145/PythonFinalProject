from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.internal_management_use_cases import (
    GetDanhSachSinhVienUseCase, DeleteSinhVienUseCase,
    GetDanhSachMonHocUseCase, DeleteMonHocUseCase,
    GetDanhSachGiangVienUseCase, DeleteGiangVienUseCase
)

class SinhVienView(APIView):
    """
    GET /api/pdt/sinh-vien
    DELETE /api/pdt/sinh-vien/<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10000))
        use_case = GetDanhSachSinhVienUseCase()
        result = use_case.execute(page, page_size)
        return Response(result.to_dict(), status=result.status_code or 200)

    def delete(self, request, id):
        use_case = DeleteSinhVienUseCase()
        result = use_case.execute(id)
        return Response(result.to_dict(), status=result.status_code or 200)

class MonHocView(APIView):
    """
    GET /api/pdt/mon-hoc
    DELETE /api/pdt/mon-hoc/<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10000))
        use_case = GetDanhSachMonHocUseCase()
        result = use_case.execute(page, page_size)
        return Response(result.to_dict(), status=result.status_code or 200)

    def delete(self, request, id):
        use_case = DeleteMonHocUseCase()
        result = use_case.execute(id)
        return Response(result.to_dict(), status=result.status_code or 200)

class GiangVienView(APIView):
    """
    GET /api/pdt/giang-vien
    DELETE /api/pdt/giang-vien/<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10000))
        use_case = GetDanhSachGiangVienUseCase()
        result = use_case.execute(page, page_size)
        return Response(result.to_dict(), status=result.status_code or 200)

    def delete(self, request, id):
        use_case = DeleteGiangVienUseCase()
        result = use_case.execute(id)
        return Response(result.to_dict(), status=result.status_code or 200)
