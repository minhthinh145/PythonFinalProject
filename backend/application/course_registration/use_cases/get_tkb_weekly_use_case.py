from datetime import date, timedelta
from typing import List, Dict, Any
from core.types import ServiceResult
from application.course_registration.interfaces import IDangKyHocPhanRepository

class GetTKBWeeklyUseCase:
    def __init__(self, dang_ky_repo: IDangKyHocPhanRepository):
        self.dang_ky_repo = dang_ky_repo

    def execute(self, sinh_vien_id: str, hoc_ky_id: str, date_start: date, date_end: date) -> ServiceResult:
        if not sinh_vien_id or not hoc_ky_id or not date_start or not date_end:
            return ServiceResult.fail(
                "Thiếu thông tin (sinh viên, học kỳ, ngày bắt đầu, ngày kết thúc)",
                error_code="MISSING_PARAMS"
            )

        # 1. Get registered classes with full related data
        registered_classes = self.dang_ky_repo.find_by_sinh_vien_and_hoc_ky(sinh_vien_id, hoc_ky_id)
        
        tkb_items = []
        
        # 2. Iterate and expand schedule
        for reg in registered_classes:
            lhp = reg.lop_hoc_phan
            
            schedules = []
            if hasattr(lhp, 'lichhocdinhky_set'):
                schedules = lhp.lichhocdinhky_set.all()
            
            if not schedules:
                continue
                
            for lich in schedules:
                current_date = date_start
                while current_date <= date_end:
                    # Python weekday(): Mon=0, Sun=6
                    # DB thu: Sun=1, Mon=2, ..., Sat=7
                    py_weekday = current_date.weekday()  # 0-6 (Mon-Sun)
                    # Convert to DB format: Sun=1, Mon=2, ..., Sat=7
                    thu_db = 2 + py_weekday if py_weekday < 6 else 1  # Sun=1
                    
                    if thu_db == lich.thu:
                        # Match! Add to items
                        # FE expects SVTKBWeeklyItemDTO format
                        item = {
                            "thu": lich.thu,
                            "tiet_bat_dau": lich.tiet_bat_dau,
                            "tiet_ket_thuc": lich.tiet_ket_thuc,
                            "phong": {
                                "id": str(lich.phong.id) if lich.phong else "",
                                "ma_phong": lich.phong.ma_phong if lich.phong else ""
                            },
                            "mon_hoc": {
                                "ma_mon": lhp.hoc_phan.mon_hoc.ma_mon,
                                "ten_mon": lhp.hoc_phan.mon_hoc.ten_mon
                            },
                            "giang_vien": lhp.giang_vien.id.ho_ten if lhp.giang_vien and lhp.giang_vien.id else None,
                            "ngay_hoc": current_date.isoformat()
                        }
                        tkb_items.append(item)
                    
                    current_date += timedelta(days=1)

        # 3. Sort by date and start period
        tkb_items.sort(key=lambda x: (x['ngay_hoc'], x['tiet_bat_dau']))

        return ServiceResult.ok(tkb_items)
