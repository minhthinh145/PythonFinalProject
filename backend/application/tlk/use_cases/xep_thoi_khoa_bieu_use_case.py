"""
Application Layer - TLK Xep Thoi Khoa Bieu Use Case
"""
from typing import List, Optional
from dataclasses import dataclass
from core.types.service_result import ServiceResult


@dataclass
class ThongTinLopHoc:
    """DTO for lop hoc info in TKB request"""
    id: Optional[str] = None
    ten_lop: str = ""
    phong_hoc: Optional[str] = None
    phong_hoc_id: Optional[str] = None
    ngay_bat_dau: Optional[str] = None
    ngay_ket_thuc: Optional[str] = None
    tiet_bat_dau: Optional[int] = None
    tiet_ket_thuc: Optional[int] = None
    thu_trong_tuan: Optional[int] = None


@dataclass
class XepTKBRequest:
    """Request DTO for xep TKB"""
    ma_hoc_phan: str
    hoc_ky_id: str
    danh_sach_lop: List[dict]


class XepThoiKhoaBieuUseCase:
    """
    Use case for TLK to create/update TKB for a học phần
    
    Business Rules:
    - TLK can only xep TKB for học phần of their khoa
    - Creates LopHocPhan and LichHocDinhKy entries
    - Validates phong_hoc availability (optional - can implement later)
    """
    
    def __init__(self, tlk_repo, tkb_repo):
        self.tlk_repo = tlk_repo
        self.tkb_repo = tkb_repo
    
    def execute(
        self,
        user_id: str,
        request: XepTKBRequest,
        giang_vien_id: Optional[str] = None
    ) -> ServiceResult:
        """
        Execute the use case
        
        Args:
            user_id: ID of TLK user
            request: XepTKBRequest with ma_hoc_phan, hoc_ky_id, danh_sach_lop
            giang_vien_id: Optional giang vien to assign
        """
        # 1. Validate TLK user
        khoa_id = self.tlk_repo.get_khoa_id_by_user(user_id)
        if not khoa_id:
            return ServiceResult.failure("Không tìm thấy thông tin khoa của trợ lý khoa")
        
        # 2. Validate request
        if not request.ma_hoc_phan:
            return ServiceResult.failure("Mã học phần không được rỗng")
        
        if not request.hoc_ky_id:
            return ServiceResult.failure("Học kỳ ID không được rỗng")
        
        if not request.danh_sach_lop:
            return ServiceResult.failure("Danh sách lớp không được rỗng")
        
        # 3. Transform danh_sach_lop from camelCase to snake_case
        transformed_lop = []
        for lop in request.danh_sach_lop:
            transformed_lop.append({
                'id': lop.get('id'),
                'tenLop': lop.get('tenLop'),
                'phongHocId': lop.get('phongHocId'),
                'ngayBatDau': lop.get('ngayBatDau'),
                'ngayKetThuc': lop.get('ngayKetThuc'),
                'tietBatDau': lop.get('tietBatDau'),
                'tietKetThuc': lop.get('tietKetThuc'),
                'thuTrongTuan': lop.get('thuTrongTuan'),
            })
        
        # 4. Call repository to create TKB
        result = self.tkb_repo.xep_thoi_khoa_bieu(
            ma_hoc_phan=request.ma_hoc_phan,
            hoc_ky_id=request.hoc_ky_id,
            danh_sach_lop=transformed_lop,
            giang_vien_id=giang_vien_id
        )
        
        if result['success']:
            # Optionally cache to MongoDB
            self._cache_to_mongodb(request.ma_hoc_phan, request.hoc_ky_id, transformed_lop)
            
            return ServiceResult.success(
                message=result['message'],
                data={'created_count': result['created_count']}
            )
        else:
            return ServiceResult.failure(result['message'])
    
    def _cache_to_mongodb(self, ma_hoc_phan: str, hoc_ky_id: str, danh_sach_lop: List[dict]):
        """Cache TKB to MongoDB for faster reads"""
        try:
            from infrastructure.persistence.mongodb_service import get_mongodb_service
            mongo = get_mongodb_service()
            
            if mongo.is_available:
                mongo.save_tkb_mon_hoc(ma_hoc_phan, hoc_ky_id, danh_sach_lop)
        except Exception:
            # MongoDB caching is optional, don't fail if it doesn't work
            pass
