from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.internal_management_use_cases import (
    GetDanhSachSinhVienUseCase, DeleteSinhVienUseCase, CreateSinhVienUseCase,
    UpdateSinhVienUseCase,
    GetDanhSachMonHocUseCase, DeleteMonHocUseCase,
    GetDanhSachGiangVienUseCase, DeleteGiangVienUseCase, CreateGiangVienUseCase,
    UpdateGiangVienUseCase
)

class SinhVienView(APIView):
    """
    GET /api/pdt/sinh-vien
    POST /api/pdt/sinh-vien
    PUT /api/pdt/sinh-vien/<id>
    DELETE /api/pdt/sinh-vien/<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10000))
        use_case = GetDanhSachSinhVienUseCase()
        result = use_case.execute(page, page_size)
        return Response(result.to_dict(), status=result.status_code or 200)
    
    def post(self, request):
        use_case = CreateSinhVienUseCase()
        result = use_case.execute(request.data)
        return Response(result.to_dict(), status=result.status_code or 201)

    def put(self, request, id):
        use_case = UpdateSinhVienUseCase()
        result = use_case.execute(id, request.data)
        return Response(result.to_dict(), status=result.status_code or 200)

    def delete(self, request, id):
        use_case = DeleteSinhVienUseCase()
        result = use_case.execute(id)
        return Response(result.to_dict(), status=result.status_code or 200)

class MonHocView(APIView):
    """
    GET /api/pdt/mon-hoc - List all
    GET /api/pdt/mon-hoc/<id> - Get detail
    DELETE /api/pdt/mon-hoc/<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            # Get single detail
            use_case = GetDanhSachMonHocUseCase()
            result = use_case.execute_single(id)
            return Response(result.to_dict(), status=result.status_code or 200)
        else:
            # Get list
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
    GET /api/pdt/giang-vien - List all
    GET /api/pdt/giang-vien/<id> - Get detail
    POST /api/pdt/giang-vien - Create new
    PUT /api/pdt/giang-vien/<id> - Update info (and password if provided)
    DELETE /api/pdt/giang-vien/<id>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            # Get single detail
            use_case = GetDanhSachGiangVienUseCase()
            result = use_case.execute_single(id)
            return Response(result.to_dict(), status=result.status_code or 200)
        else:
            # Get list
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('pageSize', 10000))
            use_case = GetDanhSachGiangVienUseCase()
            result = use_case.execute(page, page_size)
            return Response(result.to_dict(), status=result.status_code or 200)
    
    def post(self, request):
        use_case = CreateGiangVienUseCase()
        result = use_case.execute(request.data)
        return Response(result.to_dict(), status=result.status_code or 201)

    def put(self, request, id):
        use_case = UpdateGiangVienUseCase()
        result = use_case.execute(id, request.data)
        return Response(result.to_dict(), status=result.status_code or 200)

    def delete(self, request, id):
        use_case = DeleteGiangVienUseCase()
        result = use_case.execute(id)
        return Response(result.to_dict(), status=result.status_code or 200)
