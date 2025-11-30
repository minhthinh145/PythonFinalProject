from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.room_management_use_cases import (
    GetAvailablePhongHocUseCase, GetPhongHocByKhoaUseCase,
    AssignPhongToKhoaUseCase, UnassignPhongFromKhoaUseCase
)
from infrastructure.persistence.pdt.repositories import PhongHocRepository

class AvailableRoomView(APIView):
    """
    GET /api/pdt/phong-hoc/available
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        use_case = GetAvailablePhongHocUseCase(PhongHocRepository())
        result = use_case.execute()
        return Response(result.to_dict(), status=result.status_code or 200)

class RoomByKhoaView(APIView):
    """
    GET /api/pdt/phong-hoc/khoa/{khoaId}
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, khoaId):
        use_case = GetPhongHocByKhoaUseCase(PhongHocRepository())
        result = use_case.execute(khoaId)
        return Response(result.to_dict(), status=result.status_code or 200)

class AssignRoomView(APIView):
    """
    POST /api/pdt/phong-hoc/assign
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phong_id = request.data.get('phongId')
        khoa_id = request.data.get('khoaId')
        
        use_case = AssignPhongToKhoaUseCase(PhongHocRepository())
        result = use_case.execute(phong_id, khoa_id)
        return Response(result.to_dict(), status=result.status_code or 200)

class UnassignRoomView(APIView):
    """
    POST /api/pdt/phong-hoc/unassign
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phong_id = request.data.get('phongId')
        
        use_case = UnassignPhongFromKhoaUseCase(PhongHocRepository())
        result = use_case.execute(phong_id)
        return Response(result.to_dict(), status=result.status_code or 200)
