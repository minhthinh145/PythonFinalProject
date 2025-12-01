"""
Presentation Layer - TLK (Tro Ly Khoa) API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from application.tlk.use_cases import (
    GetHocPhansForCreateLopUseCase,
    GetPhongHocByTLKUseCase,
    GetAvailablePhongHocUseCase,
    CreateDeXuatHocPhanUseCase,
    CreateDeXuatHocPhanRequest,
    GetDeXuatHocPhanUseCase,
    GetTKBBatchUseCase,
    XepThoiKhoaBieuUseCase,
    XepTKBRequest,
)
from application.tlk.use_cases.get_mon_hoc_use_case import GetMonHocByKhoaUseCase
from application.tlk.use_cases.get_giang_vien_use_case import GetGiangVienByKhoaUseCase
from infrastructure.persistence.tlk.tlk_repository import (
    TLKRepository, 
    TLKHocPhanRepository,
    TLKDeXuatRepository,
    TLKThoiKhoaBieuRepository,
)


class TLKMonHocView(APIView):
    """
    Get Mon Hoc of TLK's khoa
    GET /api/tlk/mon-hoc
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = str(request.user.id)
        
        repo = TLKRepository()
        use_case = GetMonHocByKhoaUseCase(repo)
        
        result = use_case.execute(user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TLKGiangVienView(APIView):
    """
    Get Giang Vien of TLK's khoa
    GET /api/tlk/giang-vien
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = str(request.user.id)
        mon_hoc_id = request.query_params.get('mon_hoc_id')
        
        repo = TLKRepository()
        use_case = GetGiangVienByKhoaUseCase(repo)
        
        result = use_case.execute(user_id, mon_hoc_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TLKHocPhansForCreateLopView(APIView):
    """
    Get Hoc Phans available for creating Lop Hoc Phan
    GET /api/tlk/lop-hoc-phan/get-hoc-phan/<hocKyId>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, hoc_ky_id):
        user_id = str(request.user.id)
        
        tlk_repo = TLKRepository()
        hp_repo = TLKHocPhanRepository()
        use_case = GetHocPhansForCreateLopUseCase(tlk_repo, hp_repo)
        
        result = use_case.execute(user_id, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TLKPhongHocView(APIView):
    """
    Get Phong Hoc of TLK's khoa
    GET /api/tlk/phong-hoc
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = str(request.user.id)
        
        repo = TLKRepository()
        use_case = GetPhongHocByTLKUseCase(repo)
        
        result = use_case.execute(user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TLKAvailablePhongHocView(APIView):
    """
    Get available (unassigned) Phong Hoc
    GET /api/tlk/phong-hoc/available
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = str(request.user.id)
        
        repo = TLKRepository()
        use_case = GetAvailablePhongHocUseCase(repo)
        
        result = use_case.execute(user_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TLKDeXuatHocPhanView(APIView):
    """
    De Xuat Hoc Phan CRUD for TLK
    POST /api/tlk/de-xuat-hoc-phan - Create de xuat
    GET  /api/tlk/de-xuat-hoc-phan - List de xuat
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new de xuat hoc phan"""
        user_id = str(request.user.id)
        
        # Parse request body
        data = request.data
        ma_hoc_phan = data.get('maHocPhan')
        ma_giang_vien = data.get('maGiangVien')
        hoc_ky_id = data.get('hocKyId')
        
        if not ma_hoc_phan:
            return Response({
                'isSuccess': False,
                'message': 'Mã học phần không được rỗng'
            }, status=400)
        
        # Create request DTO
        req = CreateDeXuatHocPhanRequest(
            ma_hoc_phan=ma_hoc_phan,
            ma_giang_vien=ma_giang_vien or ''
        )
        
        # Execute use case
        tlk_repo = TLKRepository()
        de_xuat_repo = TLKDeXuatRepository()
        use_case = CreateDeXuatHocPhanUseCase(tlk_repo, de_xuat_repo)
        
        result = use_case.execute(user_id, req, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)
    
    def get(self, request):
        """List de xuat hoc phan of TLK's khoa"""
        user_id = str(request.user.id)
        hoc_ky_id = request.query_params.get('hocKyId')
        
        # Execute use case
        tlk_repo = TLKRepository()
        de_xuat_repo = TLKDeXuatRepository()
        use_case = GetDeXuatHocPhanUseCase(tlk_repo, de_xuat_repo)
        
        result = use_case.execute(user_id, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TLKThoiKhoaBieuBatchView(APIView):
    """
    Get TKB for multiple hoc phans
    POST /api/tlk/thoi-khoa-bieu/batch
    Body: { maHocPhans: string[], hocKyId: string }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_id = str(request.user.id)
        
        # Parse request body
        data = request.data
        ma_hoc_phans = data.get('maHocPhans', [])
        hoc_ky_id = data.get('hocKyId')
        
        if not ma_hoc_phans:
            return Response({
                'isSuccess': False,
                'message': 'Danh sách mã học phần không được rỗng'
            }, status=400)
        
        if not hoc_ky_id:
            return Response({
                'isSuccess': False,
                'message': 'Học kỳ ID không được rỗng'
            }, status=400)
        
        # Execute use case
        tkb_repo = TLKThoiKhoaBieuRepository()
        use_case = GetTKBBatchUseCase(tkb_repo)
        
        result = use_case.execute(ma_hoc_phans, hoc_ky_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class TLKXepThoiKhoaBieuView(APIView):
    """
    Xep Thoi Khoa Bieu for a hoc phan
    POST /api/tlk/thoi-khoa-bieu
    Body: { maHocPhan: string, hocKyId: string, danhSachLop: ThongTinLopHoc[] }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_id = str(request.user.id)
        
        # Parse request body
        data = request.data
        ma_hoc_phan = data.get('maHocPhan')
        hoc_ky_id = data.get('hocKyId')
        danh_sach_lop = data.get('danhSachLop', [])
        giang_vien_id = data.get('giangVienId')
        
        if not ma_hoc_phan:
            return Response({
                'isSuccess': False,
                'message': 'Mã học phần không được rỗng'
            }, status=400)
        
        if not hoc_ky_id:
            return Response({
                'isSuccess': False,
                'message': 'Học kỳ ID không được rỗng'
            }, status=400)
        
        if not danh_sach_lop:
            return Response({
                'isSuccess': False,
                'message': 'Danh sách lớp không được rỗng'
            }, status=400)
        
        # Create request DTO
        req = XepTKBRequest(
            ma_hoc_phan=ma_hoc_phan,
            hoc_ky_id=hoc_ky_id,
            danh_sach_lop=danh_sach_lop
        )
        
        # Execute use case
        tlk_repo = TLKRepository()
        tkb_repo = TLKThoiKhoaBieuRepository()
        use_case = XepThoiKhoaBieuUseCase(tlk_repo, tkb_repo)
        
        result = use_case.execute(user_id, req, giang_vien_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)
