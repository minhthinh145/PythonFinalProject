from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.tuition_policy_use_cases import (
    GetChinhSachTinChiUseCase, CreateChinhSachTinChiUseCase,
    UpdateChinhSachTinChiUseCase, TinhHocPhiHangLoatUseCase,
    DeleteChinhSachTinChiUseCase
)
from infrastructure.persistence.pdt.repositories import ChinhSachHocPhiRepository

class TuitionPolicyView(APIView):
    """
    GET /api/pdt/hoc-phi/chinh-sach
    POST /api/pdt/hoc-phi/chinh-sach
    PUT /api/pdt/hoc-phi/chinh-sach/{id}
    DELETE /api/pdt/chinh-sach-tin-chi/{id}
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        use_case = GetChinhSachTinChiUseCase(ChinhSachHocPhiRepository())
        result = use_case.execute()
        return Response(result.to_dict(), status=result.status_code or 200)

    def post(self, request):
        use_case = CreateChinhSachTinChiUseCase(ChinhSachHocPhiRepository())
        result = use_case.execute(request.data)
        return Response(result.to_dict(), status=result.status_code or 200)

    def put(self, request, id):
        use_case = UpdateChinhSachTinChiUseCase(ChinhSachHocPhiRepository())
        result = use_case.execute(id, request.data)
        return Response(result.to_dict(), status=result.status_code or 200)

    def delete(self, request, id):
        use_case = DeleteChinhSachTinChiUseCase(ChinhSachHocPhiRepository())
        result = use_case.execute(id)
        return Response(result.to_dict(), status=result.status_code or 200)

class CalculateTuitionView(APIView):
    """
    POST /api/pdt/hoc-phi/tinh-toan-hang-loat
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        hoc_ky_id = request.data.get('hoc_ky_id')
        use_case = TinhHocPhiHangLoatUseCase(ChinhSachHocPhiRepository())
        result = use_case.execute(hoc_ky_id)
        return Response(result.to_dict(), status=result.status_code or 200)
