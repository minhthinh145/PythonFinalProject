from datetime import date, timedelta
from typing import List, Dict, Any
from core.types import ServiceResult
from application.course_registration.interfaces import IDangKyHocPhanRepository
from infrastructure.persistence.mongodb_service import get_mongodb_service
import logging

logger = logging.getLogger(__name__)

class GetTKBWeeklyUseCase:
    """
    Get weekly TKB for a student.
    Schedules are fetched from MongoDB (primary source), not PostgreSQL.
    """
    def __init__(self, dang_ky_repo: IDangKyHocPhanRepository):
        self.dang_ky_repo = dang_ky_repo
        self.mongo_service = get_mongodb_service()

    def execute(self, sinh_vien_id: str, hoc_ky_id: str, date_start: date, date_end: date) -> ServiceResult:
        if not sinh_vien_id or not hoc_ky_id or not date_start or not date_end:
            return ServiceResult.fail(
                "Thiếu thông tin (sinh viên, học kỳ, ngày bắt đầu, ngày kết thúc)",
                error_code="MISSING_PARAMS"
            )

        # 1. Get registered classes for student
        registered_classes = self.dang_ky_repo.find_by_sinh_vien_and_hoc_ky(sinh_vien_id, hoc_ky_id)
        
        logger.info(f"🔍 TKB Weekly: sinh_vien_id={sinh_vien_id}, hoc_ky_id={hoc_ky_id}, registered_classes={len(registered_classes)}")
        
        if not registered_classes:
            return ServiceResult.ok([])
        
        # 2. Build MongoDB TKB map
        mongo_tkb_map = self._build_mongo_tkb_map(hoc_ky_id)
        logger.info(f"🔍 MongoDB TKB map has {len(mongo_tkb_map)} courses")
        
        tkb_items = []
        
        # 3. Generate TKB items for each day in range
        for reg in registered_classes:
            lhp = reg.lop_hoc_phan
            mon_hoc = lhp.hoc_phan.mon_hoc if lhp.hoc_phan else None
            
            if not mon_hoc:
                continue
            
            ma_mon = mon_hoc.ma_mon
            ten_lop = lhp.ma_lop
            
            # Get schedule from MongoDB
            mongo_lop = mongo_tkb_map.get(ma_mon, {}).get(ten_lop)
            
            if not mongo_lop:
                logger.debug(f"No MongoDB schedule for {ma_mon}/{ten_lop}")
                continue
            
            # Extract schedule info
            thu = mongo_lop.get('thu_trong_tuan')  # 1=CN, 2=T2, ..., 7=T7
            tiet_bat_dau = mongo_lop.get('tiet_bat_dau')
            tiet_ket_thuc = mongo_lop.get('tiet_ket_thuc')
            phong_hoc_id = mongo_lop.get('phong_hoc_id')
            ngay_bd = mongo_lop.get('ngay_bat_dau')
            ngay_kt = mongo_lop.get('ngay_ket_thuc')
            
            if not thu:
                continue
            
            logger.info(f"🔍 LHP {ten_lop}: thu={thu}, tiet={tiet_bat_dau}-{tiet_ket_thuc}")
            
            # Get room info
            phong_text = self._get_phong_name(phong_hoc_id)
            
            # Get teacher info
            gv_text = "Chưa phân công"
            if lhp.giang_vien and lhp.giang_vien.id:
                gv_text = lhp.giang_vien.id.ho_ten
            
            # Generate items for each matching day
            current_date = date_start
            while current_date <= date_end:
                # Python weekday(): Mon=0, Sun=6
                # MongoDB thu: CN=1, T2=2, ..., T7=7
                py_weekday = current_date.weekday()
                thu_db = 2 + py_weekday if py_weekday < 6 else 1  # Sun=1
                
                if thu_db == thu:
                    # Also check if date is within schedule's date range
                    if self._is_within_schedule_range(current_date, ngay_bd, ngay_kt):
                        item = {
                            "thu": thu,
                            "tiet_bat_dau": tiet_bat_dau,
                            "tiet_ket_thuc": tiet_ket_thuc,
                            "phong": {
                                "id": str(phong_hoc_id) if phong_hoc_id else "",
                                "ma_phong": phong_text
                            },
                            "mon_hoc": {
                                "ma_mon": ma_mon,
                                "ten_mon": mon_hoc.ten_mon
                            },
                            "giang_vien": gv_text,
                            "ngay_hoc": current_date.isoformat()
                        }
                        tkb_items.append(item)
                
                current_date += timedelta(days=1)

        # 4. Sort by date and start period
        tkb_items.sort(key=lambda x: (x['ngay_hoc'], x['tiet_bat_dau'] or 0))
        
        logger.info(f"🔍 TKB Items generated: {len(tkb_items)}")

        return ServiceResult.ok(tkb_items)
    
    def _build_mongo_tkb_map(self, hoc_ky_id: str) -> Dict[str, Dict]:
        """Build a map of maHocPhan -> { tenLop -> tkb_info } from MongoDB"""
        tkb_map = {}
        
        if not self.mongo_service.is_available:
            logger.warning("MongoDB not available, TKB will be empty")
            return tkb_map
        
        try:
            all_tkb = self.mongo_service.get_tkb_by_hoc_ky(hoc_ky_id, transform_to_camel=False)
            
            for tkb_doc in all_tkb:
                ma_hoc_phan = tkb_doc.get('ma_hoc_phan')
                danh_sach_lop = tkb_doc.get('danhSachLop', [])
                
                if ma_hoc_phan not in tkb_map:
                    tkb_map[ma_hoc_phan] = {}
                
                for lop in danh_sach_lop:
                    ten_lop = lop.get('ten_lop')
                    if ten_lop:
                        tkb_map[ma_hoc_phan][ten_lop] = lop
            
        except Exception as e:
            logger.error(f"Failed to build TKB map: {e}")
        
        return tkb_map
    
    def _get_phong_name(self, phong_hoc_id) -> str:
        """Get room name from ID"""
        if not phong_hoc_id:
            return "TBA"
        
        try:
            from infrastructure.persistence.models import Phong
            phong = Phong.objects.using('neon').filter(id=phong_hoc_id).first()
            if phong:
                return phong.ma_phong
        except Exception as e:
            logger.error(f"Failed to get phong name: {e}")
        
        return "TBA"
    
    def _is_within_schedule_range(self, check_date: date, ngay_bd, ngay_kt) -> bool:
        """Check if date is within schedule's date range"""
        try:
            # Parse ngay_bat_dau
            if ngay_bd:
                if hasattr(ngay_bd, 'date'):
                    start_date = ngay_bd.date()
                elif isinstance(ngay_bd, date):
                    start_date = ngay_bd
                else:
                    from datetime import datetime
                    start_date = datetime.fromisoformat(str(ngay_bd).replace('Z', '+00:00')).date()
                
                if check_date < start_date:
                    return False
            
            # Parse ngay_ket_thuc
            if ngay_kt:
                if hasattr(ngay_kt, 'date'):
                    end_date = ngay_kt.date()
                elif isinstance(ngay_kt, date):
                    end_date = ngay_kt
                else:
                    from datetime import datetime
                    end_date = datetime.fromisoformat(str(ngay_kt).replace('Z', '+00:00')).date()
                
                if check_date > end_date:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error parsing schedule dates: {e}")
            return True  # Default to include if can't parse


