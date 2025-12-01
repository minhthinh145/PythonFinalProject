"""
Infrastructure Layer - GV TKB Repository Implementation
"""
from typing import List
from datetime import date
from application.gv.interfaces import (
    IGVTKBRepository,
    GVTKBItemDTO,
)
from infrastructure.persistence.models import (
    LichDayLopHocPhan,
    LopHocPhan,
)


class GVTKBRepository(IGVTKBRepository):
    """
    Repository implementation for GV's TKB (Timetable) operations
    Uses Django ORM with PostgreSQL (Neon)
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
        """
        # Get timetable entries within date range
        lich_day_list = LichDayLopHocPhan.objects.using('neon').select_related(
            'lop_hoc_phan',
            'lop_hoc_phan__hoc_phan',
            'lop_hoc_phan__hoc_phan__mon_hoc',
            'phong',
        ).filter(
            lop_hoc_phan__giang_vien__id=gv_user_id,
            lop_hoc_phan__hoc_phan__id_hoc_ky=hoc_ky_id,
            ngay_hoc__gte=date_start,
            ngay_hoc__lte=date_end,
        ).order_by('ngay_hoc', 'tiet_bat_dau')
        
        result = []
        for lich in lich_day_list:
            lhp = lich.lop_hoc_phan
            hoc_phan = lhp.hoc_phan if lhp else None
            mon_hoc = hoc_phan.mon_hoc if hoc_phan else None
            
            result.append(GVTKBItemDTO(
                lop_hoc_phan_id=str(lhp.id) if lhp else None,
                ma_lop=lhp.ma_lop if lhp else None,
                ten_mon=mon_hoc.ten_mon if mon_hoc else None,
                ma_mon=mon_hoc.ma_mon if mon_hoc else None,
                phong=lich.phong.ten_phong if lich.phong else None,
                thu=lich.thu or lich.ngay_hoc.weekday() + 2,  # Convert to VN weekday (2=Mon)
                tiet_bat_dau=lich.tiet_bat_dau,
                tiet_ket_thuc=lich.tiet_ket_thuc,
                ngay_hoc=lich.ngay_hoc.isoformat() if lich.ngay_hoc else None,
            ))
        
        return result
