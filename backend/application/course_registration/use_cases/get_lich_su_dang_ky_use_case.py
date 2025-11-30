from core.types import ServiceResult
from application.course_registration.interfaces import ILichSuDangKyRepository

class GetLichSuDangKyUseCase:
    def __init__(self, lich_su_repo: ILichSuDangKyRepository):
        self.lich_su_repo = lich_su_repo

    def execute(self, sinh_vien_id: str, hoc_ky_id: str) -> ServiceResult:
        if not sinh_vien_id or not hoc_ky_id:
            return ServiceResult.fail(
                "Thiếu thông tin (sinh viên, học kỳ)",
                error_code="MISSING_PARAMS"
            )

        # Get history record
        lich_su = self.lich_su_repo.find_by_sinh_vien_and_hoc_ky(sinh_vien_id, hoc_ky_id)
        
        logs = []
        if lich_su:
            # Assuming lich_su has a relation to details
            # In Django ORM: lich_su.chitietlichsudangky_set.all()
            # We need to be careful about how repo returns data.
            # If repo returns model instance, we can access relation.
            
            for detail in lich_su.chitietlichsudangky_set.all():
                log_item = {
                    "thoiGian": detail.thoi_gian, # Need to format?
                    "hanhDong": detail.hanh_dong,
                    "monHoc": "",
                    "maLop": ""
                }
                
                if detail.dang_ky_hoc_phan and detail.dang_ky_hoc_phan.lop_hoc_phan:
                    lhp = detail.dang_ky_hoc_phan.lop_hoc_phan
                    log_item["maLop"] = lhp.ma_lop
                    log_item["tenLop"] = lhp.ten_lop_hoc_phan if hasattr(lhp, 'ten_lop_hoc_phan') else lhp.ma_lop
                    # Assuming we can access subject name via relation
                    # lhp.hoc_phan.mon_hoc.ten_mon_hoc
                    
                logs.append(log_item)

        return ServiceResult.ok({"logs": logs})
