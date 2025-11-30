from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from application.pdt.use_cases.get_de_xuat_hoc_phan_use_case import GetDeXuatHocPhanUseCase
from application.pdt.use_cases.duyet_de_xuat_hoc_phan_use_case import DuyetDeXuatHocPhanUseCase
from infrastructure.persistence.pdt.repositories import DeXuatHocPhanRepository

class CourseProposalView(APIView):
    """
    GET /api/pdt/de-xuat-hoc-phan
    PATCH /api/pdt/de-xuat-hoc-phan/duyet
    """
    permission_classes = [IsAuthenticated] # TODO: Add Role Check

    def get(self, request):
        use_case = GetDeXuatHocPhanUseCase(DeXuatHocPhanRepository())
        result = use_case.execute()
        return Response(result.to_dict(), status=result.status_code or 200)

    def patch(self, request):
        if 'tu-choi' in request.path:
            from application.pdt.use_cases.tu_choi_de_xuat_hoc_phan_use_case import TuChoiDeXuatHocPhanUseCase
            
            proposal_id = request.data.get('id')
            reason = request.data.get('lyDo') # Expecting 'lyDo' from FE
            
            use_case = TuChoiDeXuatHocPhanUseCase(DeXuatHocPhanRepository())
            result = use_case.execute(proposal_id, reason)
            return Response(result.to_dict(), status=result.status_code or 200)
        else:
            # Default to approve
            proposal_id = request.data.get('id')
            use_case = DuyetDeXuatHocPhanUseCase(DeXuatHocPhanRepository())
            result = use_case.execute(proposal_id)
            return Response(result.to_dict(), status=result.status_code or 200)
