from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.toggle_phase_use_case import TogglePhaseUseCase
from application.pdt.use_cases.reset_demo_data_use_case import ResetDemoDataUseCase

class TogglePhaseView(APIView):
    """
    POST /api/pdt/demo/toggle-phase
    Body: { "hocKyId": "...", "phase": "..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        hoc_ky_id = request.data.get('hocKyId')
        phase = request.data.get('phase')
        
        if not phase:
            return Response({
                "isSuccess": False,
                "message": "phase is required"
            }, status=400)
            
        use_case = TogglePhaseUseCase()
        result = use_case.execute(hoc_ky_id, phase)
        
        return Response(result.to_dict(), status=result.status_code or 200)

    def patch(self, request):
        return self.post(request)


class ResetDemoDataView(APIView):
    """
    POST /api/pdt/demo/reset-data
    Body: { "confirmReset": true }
    
    Clears all test/demo data while preserving master data:
    - Keeps: users, mon_hoc, khoa, phong, hoc_ky, nien_khoa, etc.
    - Clears: registrations, payments, schedules, proposals, etc.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        confirm_reset = request.data.get('confirmReset', False)
        
        if not confirm_reset:
            return Response({
                "isSuccess": False,
                "message": "Phải xác nhận reset (confirmReset=true). Hành động này sẽ xóa toàn bộ dữ liệu demo!",
                "errorCode": "CONFIRMATION_REQUIRED"
            }, status=400)
        
        use_case = ResetDemoDataUseCase()
        result = use_case.execute(confirm_reset=True)
        
        return Response(result.to_dict(), status=result.status_code or 200)

