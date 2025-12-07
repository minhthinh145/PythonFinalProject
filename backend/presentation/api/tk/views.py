"""
Presentation Layer - TK (Truong Khoa) API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from application.tk.use_cases import (
    GetDeXuatHocPhanForTKUseCase,
    DuyetDeXuatHocPhanByTKUseCase,
    TuChoiDeXuatHocPhanByTKUseCase,
)
from infrastructure.persistence.tk.tk_repository import (
    TKTruongKhoaRepository,
    TKDeXuatHocPhanRepository,
)


class TKDeXuatHocPhanView(APIView):
    """
    Get De Xuat Hoc Phan for Truong Khoa
    GET /api/tk/de-xuat-hoc-phan
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of de xuat hoc phan waiting for TK approval"""
        user_id = str(request.user.id)
        
        tk_repo = TKTruongKhoaRepository()
        de_xuat_repo = TKDeXuatHocPhanRepository()
        
        use_case = GetDeXuatHocPhanForTKUseCase(tk_repo, de_xuat_repo)
        result = use_case.execute(user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TKDuyetDeXuatView(APIView):
    """
    Duyet De Xuat Hoc Phan by Truong Khoa
    PATCH /api/tk/de-xuat-hoc-phan/duyet
    Body: { "id": "uuid" }
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        """Approve a de xuat hoc phan"""
        user_id = str(request.user.id)
        de_xuat_id = request.data.get('id')
        
        if not de_xuat_id:
            return Response({
                'isSuccess': False,
                'message': 'ID đề xuất học phần không được rỗng'
            }, status=400)
        
        tk_repo = TKTruongKhoaRepository()
        de_xuat_repo = TKDeXuatHocPhanRepository()
        
        use_case = DuyetDeXuatHocPhanByTKUseCase(tk_repo, de_xuat_repo)
        result = use_case.execute(user_id, de_xuat_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TKTuChoiDeXuatView(APIView):
    """
    Tu Choi De Xuat Hoc Phan by Truong Khoa
    PATCH /api/tk/de-xuat-hoc-phan/tu-choi
    Body: { "id": "uuid" }
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        """Reject a de xuat hoc phan"""
        user_id = str(request.user.id)
        de_xuat_id = request.data.get('id')
        
        if not de_xuat_id:
            return Response({
                'isSuccess': False,
                'message': 'ID đề xuất học phần không được rỗng'
            }, status=400)
        
        tk_repo = TKTruongKhoaRepository()
        de_xuat_repo = TKDeXuatHocPhanRepository()
        
        use_case = TuChoiDeXuatHocPhanByTKUseCase(tk_repo, de_xuat_repo)
        result = use_case.execute(user_id, de_xuat_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)
