"""
Application Layer - GV Use Case: Get TKB Weekly
Fetches schedules from MongoDB (primary source)
"""
from core.types import ServiceResult
from application.gv.interfaces import IGVTKBRepository, GVTKBItemDTO
from infrastructure.persistence.mongodb_service import get_mongodb_service
from datetime import date, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GetGVTKBWeeklyUseCase:
    """
    Use case to get weekly timetable for a GiangVien
    Schedules are fetched from MongoDB (primary source)
    """
    
    def __init__(self, tkb_repository: IGVTKBRepository):
        self.tkb_repository = tkb_repository
        self.mongo_service = get_mongodb_service()
    
    def execute(
        self, 
        gv_user_id: str, 
        hoc_ky_id: str,
        date_start: date,
        date_end: date
    ) -> ServiceResult:
        """
        Execute get TKB weekly logic using MongoDB
        """
        try:
            from infrastructure.persistence.models import LopHocPhan
            
            # 1. Get LopHocPhan assigned to this GV
            lop_hoc_phans = LopHocPhan.objects.using('neon').select_related(
                'hoc_phan',
                'hoc_phan__mon_hoc',
            ).filter(
                giang_vien_id=gv_user_id,
                hoc_phan__id_hoc_ky=hoc_ky_id,
            )
            
            logger.info(f"🔍 GV TKB: gv_user_id={gv_user_id}, hoc_ky_id={hoc_ky_id}, lop_count={lop_hoc_phans.count()}")
            
            if not lop_hoc_phans.exists():
                return ServiceResult.ok([])
            
            # 2. Build MongoDB TKB map
            mongo_tkb_map = self._build_mongo_tkb_map(hoc_ky_id)
            logger.info(f"🔍 MongoDB TKB map has {len(mongo_tkb_map)} courses")
            
            tkb_items = []
            
            # 3. Generate TKB items for each LopHocPhan
            for lop in lop_hoc_phans:
                mon_hoc = lop.hoc_phan.mon_hoc if lop.hoc_phan else None
                if not mon_hoc:
                    continue
                
                ma_mon = mon_hoc.ma_mon
                ten_lop = lop.ma_lop
                
                # Get schedule from MongoDB
                mongo_lop = mongo_tkb_map.get(ma_mon, {}).get(ten_lop)
                
                if not mongo_lop:
                    logger.debug(f"No MongoDB schedule for {ma_mon}/{ten_lop}")
                    continue
                
                thu = mongo_lop.get('thu_trong_tuan')
                tiet_bat_dau = mongo_lop.get('tiet_bat_dau')
                tiet_ket_thuc = mongo_lop.get('tiet_ket_thuc')
                phong_hoc_id = mongo_lop.get('phong_hoc_id')
                ngay_bd = mongo_lop.get('ngay_bat_dau')
                ngay_kt = mongo_lop.get('ngay_ket_thuc')
                
                if not thu:
                    continue
                
                logger.info(f"🔍 LHP {ten_lop}: thu={thu}, tiet={tiet_bat_dau}-{tiet_ket_thuc}")
                
                phong_text = self._get_phong_name(phong_hoc_id)
                
                # Generate items for each matching day
                current_date = date_start
                while current_date <= date_end:
                    py_weekday = current_date.weekday()
                    thu_db = 2 + py_weekday if py_weekday < 6 else 1
                    
                    if thu_db == thu:
                        if self._is_within_schedule_range(current_date, ngay_bd, ngay_kt):
                            tkb_items.append({
                                "thu": thu,
                                "tiet_bat_dau": tiet_bat_dau,
                                "tiet_ket_thuc": tiet_ket_thuc,
                                "phong": {
                                    "id": str(phong_hoc_id) if phong_hoc_id else "",
                                    "ma_phong": phong_text
                                },
                                "lop_hoc_phan": {
                                    "id": str(lop.id),
                                    "ma_lop": lop.ma_lop,
                                },
                                "mon_hoc": {
                                    "ma_mon": ma_mon,
                                    "ten_mon": mon_hoc.ten_mon,
                                },
                                "ngay_hoc": current_date.isoformat(),
                            })
                    
                    current_date += timedelta(days=1)
            
            # Sort by date and start period
            tkb_items.sort(key=lambda x: (x['ngay_hoc'], x['tiet_bat_dau'] or 0))
            
            logger.info(f"🔍 GV TKB Items generated: {len(tkb_items)}")
            
            return ServiceResult.ok(tkb_items)
            
        except Exception as e:
            logger.error(f"Error in GV TKB weekly: {e}")
            return ServiceResult.fail(str(e))
    
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
            return True

    def _map_to_response(self, item: GVTKBItemDTO) -> Dict[str, Any]:
        """Map DTO to snake_case response (matches FE TKBWeeklyItemDTO)"""
        return {
            "thu": item.thu,
            "tiet_bat_dau": item.tiet_bat_dau,
            "tiet_ket_thuc": item.tiet_ket_thuc,
            "phong": {
                "id": item.phong_id or "",
                "ma_phong": item.ma_phong or "",
            },
            "lop_hoc_phan": {
                "id": item.lop_hoc_phan_id,
                "ma_lop": item.ma_lop,
            },
            "mon_hoc": {
                "ma_mon": item.ma_mon,
                "ten_mon": item.ten_mon,
            },
            "ngay_hoc": item.ngay_hoc,
        }

