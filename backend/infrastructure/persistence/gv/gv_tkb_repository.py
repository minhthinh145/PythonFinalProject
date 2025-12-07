"""
Infrastructure Layer - GV TKB Repository Implementation
"""
from typing import List
from datetime import date, timedelta
from application.gv.interfaces import (
    IGVTKBRepository,
    GVTKBItemDTO,
)
from infrastructure.persistence.models import (
    LopHocPhan,
    LichHocDinhKy,
)


class GVTKBRepository(IGVTKBRepository):
    """
    Repository implementation for GV's TKB (Timetable) operations
    Uses Django ORM with PostgreSQL (Neon)
    
    Logic: Query LichHocDinhKy (recurring schedules) and generate 
    TKB entries for each day in date range that matches the weekday
    """
    
    def get_tkb_weekly(
        self, 
        gv_user_id: str,
        hoc_ky_id: str,
        date_start: date,
        date_end: date
    ) -> List[GVTKBItemDTO]:
        """
        Get weekly timetable for a GiangVien
        
        Algorithm (same as legacy):
        1. Get LopHocPhan of GV in HocKy with LichHocDinhKy (recurring)
        2. For each lich_hoc_dinh_ky, generate TKB entries for days matching thu
        3. VN weekday: CN=1, T2=2, T3=3, ..., T7=7
        """
        print(f"🔍 TKB Query: gv_user_id={gv_user_id}, hoc_ky_id={hoc_ky_id}, date_range={date_start} to {date_end}")
        
        # Get LopHocPhan with LichHocDinhKy (recurring schedules)
        lop_hoc_phans = LopHocPhan.objects.using('neon').select_related(
            'hoc_phan',
            'hoc_phan__mon_hoc',
        ).prefetch_related(
            'lichhocdinhky_set',
            'lichhocdinhky_set__phong',
        ).filter(
            giang_vien_id=gv_user_id,  # giang_vien_id IS the user_id
            hoc_phan__id_hoc_ky=hoc_ky_id,
        )
        
        print(f"🔍 LopHocPhan found: {lop_hoc_phans.count()}")
        
        result = []
        
        for lop in lop_hoc_phans:
            hoc_phan = lop.hoc_phan
            mon_hoc = hoc_phan.mon_hoc if hoc_phan else None
            
            # Get recurring schedules
            lich_dinh_ky_list = lop.lichhocdinhky_set.all()
            print(f"  📖 Lớp {lop.ma_lop}: {lich_dinh_ky_list.count()} lịch định kỳ")
            
            if not lich_dinh_ky_list:
                continue
            
            for lich in lich_dinh_ky_list:
                # Generate TKB entries for each day in range that matches thu
                current_date = date_start
                while current_date <= date_end:
                    # Convert Python weekday to VN thu: Mon=0->2, Tue=1->3, ..., Sun=6->1
                    py_weekday = current_date.weekday()  # Mon=0, Sun=6
                    vn_thu = py_weekday + 2 if py_weekday < 6 else 1  # CN=1
                    
                    if vn_thu == lich.thu:
                        result.append(GVTKBItemDTO(
                            lop_hoc_phan_id=str(lop.id),
                            ma_lop=lop.ma_lop,
                            ten_mon=mon_hoc.ten_mon if mon_hoc else None,
                            ma_mon=mon_hoc.ma_mon if mon_hoc else None,
                            phong_id=str(lich.phong.id) if lich.phong else None,
                            ma_phong=lich.phong.ma_phong if lich.phong else None,
                            thu=lich.thu,
                            tiet_bat_dau=lich.tiet_bat_dau,
                            tiet_ket_thuc=lich.tiet_ket_thuc,
                            ngay_hoc=current_date.isoformat(),
                        ))
                    
                    current_date += timedelta(days=1)
        
        # Sort by ngay_hoc, then tiet_bat_dau
        result.sort(key=lambda x: (x.ngay_hoc or '', x.tiet_bat_dau or 0))
        
        print(f"🔍 TKB entries generated: {len(result)}")
        return result
