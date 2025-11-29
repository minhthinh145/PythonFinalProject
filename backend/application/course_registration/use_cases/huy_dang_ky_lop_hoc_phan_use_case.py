"""
Application Layer - Huy Dang Ky Lop Hoc Phan Use Case
"""
from datetime import datetime
from core.types import ServiceResult
from application.course_registration.interfaces import (
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository,
    ILopHocPhanRepository
)
from application.enrollment.interfaces import IDotDangKyRepository
from django.db import transaction

class HuyDangKyLopHocPhanUseCase:
    """
    Use case to cancel course registration
    """
    
    def __init__(
        self,
        dang_ky_hp_repo: IDangKyHocPhanRepository,
        dot_dang_ky_repo: IDotDangKyRepository,
        dang_ky_tkb_repo: IDangKyTKBRepository,
        lich_su_repo: ILichSuDangKyRepository,
        lop_hoc_phan_repo: ILopHocPhanRepository
    ):
        self.dang_ky_hp_repo = dang_ky_hp_repo
        self.dot_dang_ky_repo = dot_dang_ky_repo
        self.dang_ky_tkb_repo = dang_ky_tkb_repo
        self.lich_su_repo = lich_su_repo
        self.lop_hoc_phan_repo = lop_hoc_phan_repo

    def execute(self, request_data: dict, user_id: str) -> ServiceResult:
        """
        Execute cancellation logic
        """
        lop_hoc_phan_id = request_data.get('lopHocPhanId')
        
        if not lop_hoc_phan_id:
            return ServiceResult.fail("Thiếu ID lớp học phần", error_code="INVALID_INPUT")

        # 1. Check Dang Ky exists
        dang_ky = self.dang_ky_hp_repo.find_by_sinh_vien_and_lop_hoc_phan(user_id, lop_hoc_phan_id)
        if not dang_ky:
            return ServiceResult.fail("Không tìm thấy record đăng ký học phần", error_code="DANG_KY_NOT_FOUND")

        if dang_ky.trang_thai == "da_huy":
            return ServiceResult.fail("Đăng ký học phần đã được hủy trước đó", error_code="ALREADY_CANCELLED")

        # 2. Check Deadline
        hoc_ky_id = str(dang_ky.lop_hoc_phan.hoc_phan.id_hoc_ky)
        dot_dang_ky = self.dot_dang_ky_repo.find_active_dot_dang_ky(hoc_ky_id)
        
        if not dot_dang_ky:
            return ServiceResult.fail("Không trong đợt đăng ký học phần", error_code="NOT_IN_DANG_KY_DOT")
            
        if dot_dang_ky.han_huy_den:
            now = datetime.now()
            # Assuming han_huy_den is naive or aware, comparison needs care. 
            # For simplicity assuming compatible types or relying on repo to return aware datetime if Django settings use TZ.
            # Here we just compare.
            if now.timestamp() > dot_dang_ky.han_huy_den.timestamp():
                 return ServiceResult.fail("Đã quá hạn hủy đăng ký học phần", error_code="PAST_CANCEL_DEADLINE")

        # 3. Transaction
        try:
            with transaction.atomic():
                # 3.1 Update Status
                self.dang_ky_hp_repo.update_status(str(dang_ky.id), "da_huy")
                
                # 3.2 Delete TKB
                self.dang_ky_tkb_repo.delete_by_dang_ky_id(str(dang_ky.id))
                
                # 3.3 Log History
                self.lich_su_repo.upsert_and_log(
                    user_id,
                    hoc_ky_id,
                    str(dang_ky.id),
                    "huy_dang_ky"
                )
                
                # 3.4 Decrement Slot
                self.lop_hoc_phan_repo.update_so_luong(lop_hoc_phan_id, -1)
                
            return ServiceResult.ok(None, "Hủy đăng ký học phần thành công")
            
        except Exception as e:
            print(f"Error cancelling registration: {e}")
            return ServiceResult.fail("Lỗi khi hủy đăng ký học phần", error_code="INTERNAL_ERROR")
