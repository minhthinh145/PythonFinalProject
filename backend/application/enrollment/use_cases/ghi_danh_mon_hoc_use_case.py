"""
Application Layer - Ghi Danh Mon Hoc Use Case
"""
from core.types import ServiceResult
from application.enrollment.interfaces import (
    IHocPhanRepository,
    IGhiDanhRepository
)

class GhiDanhMonHocUseCase:
    """
    Use case to enroll in a subject
    """
    
    def __init__(
        self,
        hoc_phan_repo: IHocPhanRepository,
        ghi_danh_repo: IGhiDanhRepository
    ):
        self.hoc_phan_repo = hoc_phan_repo
        self.ghi_danh_repo = ghi_danh_repo
        
    def execute(self, request_data: dict, user_id: str) -> ServiceResult:
        """
        Execute enrollment
        """
        mon_hoc_id = request_data.get('monHocId')
        if not mon_hoc_id:
            return ServiceResult.fail("Mã học phần không hợp lệ", error_code="INVALID_INPUT")
            
        # 1. Check subject exists and is open
        hoc_phan = self.hoc_phan_repo.find_by_id(mon_hoc_id)
        if not hoc_phan:
            return ServiceResult.fail("Không tìm thấy học phần", error_code="HOC_PHAN_NOT_FOUND")
            
        if not hoc_phan.trang_thai_mo:
            return ServiceResult.fail("Học phần đã đóng, không thể ghi danh", error_code="HOC_PHAN_CLOSED")
            
        # 2. Check if already registered
        is_registered = self.ghi_danh_repo.is_already_registered(user_id, mon_hoc_id)
        if is_registered:
            return ServiceResult.fail("Bạn đã ghi danh học phần này rồi", error_code="ALREADY_REGISTERED")
            
        # 3. Create registration
        self.ghi_danh_repo.create({
            'sinh_vien_id': user_id,
            'hoc_phan_id': mon_hoc_id,
            'trang_thai': 'da_ghi_danh'
        })
        
        return ServiceResult.ok(None, "Ghi danh môn học thành công")
