from typing import List, Dict, Any, Optional
from application.enrollment.interfaces.repositories import IHocPhanRepository
from core.types.service_result import ServiceResult
from infrastructure.persistence.mongodb_service import get_mongodb_service
import logging

logger = logging.getLogger(__name__)


class TraCuuHocPhanUseCase:
    """
    Use case for tra cứu học phần - view available courses
    
    TKB data flow:
    - TKB is stored in MongoDB collection 'thoi_khoa_bieu_mon_hoc'
    - Each document has: ma_hoc_phan, hoc_ky_id, danhSachLop[]
    - We need to match MongoDB TKB with PostgreSQL LopHocPhan by ma_lop/ten_lop
    """
    
    def __init__(self, hoc_phan_repo: IHocPhanRepository):
        self.hoc_phan_repo = hoc_phan_repo
        self.mongo_service = get_mongodb_service()

    def execute(self, hoc_ky_id: str) -> ServiceResult[List[Dict[str, Any]]]:
        """
        Tra cứu học phần - grouped by mon_hoc with list of lop_hoc_phan
        
        FE expects array of:
        {
            stt: number,
            maMon: string,
            tenMon: string,
            soTinChi: number,
            loaiMon: "chuyen_nganh" | "dai_cuong" | "tu_chon",
            danhSachLop: [{
                id: string,
                maLop: string,
                giangVien: string,
                soLuongToiDa: number,
                soLuongHienTai: number,
                conSlot: number,
                thoiKhoaBieu: string
            }]
        }
        """
        try:
            # Get all LopHocPhan for this hoc_ky, grouped by mon_hoc
            lop_hoc_phans = self.hoc_phan_repo.find_lop_hoc_phan_by_hoc_ky(hoc_ky_id)
            
            # Build MongoDB TKB map for fast lookup
            mongo_tkb_map = self._build_mongo_tkb_map(hoc_ky_id)
            logger.debug(f"[TRA_CUU] Built TKB map with {len(mongo_tkb_map)} môn học")
            
            # Group by mon_hoc
            mon_hoc_map: Dict[str, Dict[str, Any]] = {}
            
            for lhp in lop_hoc_phans:
                mon_hoc = lhp.hoc_phan.mon_hoc if lhp.hoc_phan else None
                if not mon_hoc:
                    continue
                    
                mon_hoc_id = str(mon_hoc.id)
                ma_mon = mon_hoc.ma_mon or ""
                
                if mon_hoc_id not in mon_hoc_map:
                    # Determine loaiMon
                    loai_mon = "dai_cuong"  # default
                    if hasattr(mon_hoc, 'loai_mon') and mon_hoc.loai_mon:
                        loai_mon = mon_hoc.loai_mon
                    elif hasattr(mon_hoc, 'loai') and mon_hoc.loai:
                        loai_mon = mon_hoc.loai
                    
                    mon_hoc_map[mon_hoc_id] = {
                        "maMon": ma_mon,
                        "tenMon": mon_hoc.ten_mon or "",
                        "soTinChi": mon_hoc.so_tin_chi or 0,
                        "loaiMon": loai_mon,
                        "danhSachLop": []
                    }
                
                # Get TKB from MongoDB (primary source)
                tkb_string = self._get_tkb_for_lop(ma_mon, lhp.ma_lop, mongo_tkb_map, lhp)
                
                # Get giangVien - GiangVien.id is OneToOne with Users
                giang_vien_name = ""
                if hasattr(lhp, 'giang_vien') and lhp.giang_vien:
                    # Access ho_ten via the Users relation (GiangVien.id -> Users)
                    gv = lhp.giang_vien
                    if hasattr(gv, 'id') and gv.id:
                        # gv.id is the Users instance
                        giang_vien_name = getattr(gv.id, 'ho_ten', '') or ''
                
                # Get current enrollment count
                so_luong_hien_tai = 0
                if hasattr(lhp, 'dangkyhocphan_set'):
                    so_luong_hien_tai = lhp.dangkyhocphan_set.count()
                
                so_luong_toi_da = lhp.so_luong_toi_da or 50
                
                lop_item = {
                    "id": str(lhp.id),
                    "maLop": lhp.ma_lop or "",
                    "giangVien": giang_vien_name,
                    "soLuongToiDa": so_luong_toi_da,
                    "soLuongHienTai": so_luong_hien_tai,
                    "conSlot": max(0, so_luong_toi_da - so_luong_hien_tai),
                    "thoiKhoaBieu": tkb_string
                }
                
                mon_hoc_map[mon_hoc_id]["danhSachLop"].append(lop_item)
            
            # Convert to list with stt
            result = []
            for idx, (mon_id, mon_data) in enumerate(mon_hoc_map.items(), start=1):
                mon_data["stt"] = idx
                result.append(mon_data)
            
            # Return array directly (FE expects array, not wrapped object)
            return ServiceResult.ok(result)
        except Exception as e:
            logger.error(f"[TRA_CUU] Error: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult.fail(str(e))
    
    def _build_mongo_tkb_map(self, hoc_ky_id: str) -> Dict[str, Dict]:
        """
        Build a map of ma_mon -> { ten_lop -> tkb_info }
        from MongoDB thoi_khoa_bieu_mon_hoc collection
        """
        tkb_map = {}
        
        if not self.mongo_service.is_available:
            logger.warning("[TRA_CUU] MongoDB not available, TKB will be empty")
            return tkb_map
        
        try:
            # Get all TKB for this semester (snake_case for internal processing)
            all_tkb = self.mongo_service.get_tkb_by_hoc_ky(hoc_ky_id, transform_to_camel=False)
            logger.debug(f"[TRA_CUU] Found {len(all_tkb)} TKB documents in MongoDB")
            
            for tkb_doc in all_tkb:
                ma_hoc_phan = tkb_doc.get('ma_hoc_phan')
                danh_sach_lop = tkb_doc.get('danhSachLop', [])
                
                if ma_hoc_phan not in tkb_map:
                    tkb_map[ma_hoc_phan] = {}
                
                for lop in danh_sach_lop:
                    # MongoDB uses snake_case internally
                    ten_lop = lop.get('ten_lop')
                    if ten_lop:
                        # Store all sessions for this class (same class can have multiple days)
                        if ten_lop not in tkb_map[ma_hoc_phan]:
                            tkb_map[ma_hoc_phan][ten_lop] = []
                        tkb_map[ma_hoc_phan][ten_lop].append(lop)
            
            logger.debug(f"[TRA_CUU] Built TKB map with {len(tkb_map)} môn học")
            
        except Exception as e:
            logger.error(f"[TRA_CUU] Failed to build TKB map: {e}")
        
        return tkb_map
    
    def _get_tkb_for_lop(
        self, 
        ma_mon: str, 
        ten_lop: str, 
        mongo_tkb_map: Dict,
        lhp: Any
    ) -> str:
        """
        Get formatted TKB string for a specific class
        Priority: MongoDB > "Chưa có TKB"
        """
        # Try MongoDB first
        mongo_sessions = mongo_tkb_map.get(ma_mon, {}).get(ten_lop)
        
        if mongo_sessions:
            # Format all sessions for this class
            tkb_lines = []
            for session in mongo_sessions:
                line = self._format_mongo_session(session, lhp)
                if line:
                    tkb_lines.append(line)
            
            if tkb_lines:
                return "\n".join(tkb_lines)
        
        return "Chưa có TKB"
    
    def _format_mongo_session(self, session: Dict, lhp: Any) -> Optional[str]:
        """
        Format a single MongoDB TKB session to string
        
        MongoDB fields (snake_case):
        - ten_lop, phong_hoc_id, ngay_bat_dau, ngay_ket_thuc, tiet_bat_dau, tiet_ket_thuc, thu_trong_tuan
        """
        try:
            thu = session.get('thu_trong_tuan')
            tiet_bat_dau = session.get('tiet_bat_dau')
            tiet_ket_thuc = session.get('tiet_ket_thuc')
            phong_hoc_id = session.get('phong_hoc_id')
            
            # Get dates
            ngay_bd = session.get('ngay_bat_dau')
            ngay_kt = session.get('ngay_ket_thuc')
            
            # Format dates
            ngay_bd_str = self._format_date(ngay_bd)
            ngay_kt_str = self._format_date(ngay_kt)
            
            # Get room name
            phong_text = self._get_phong_name(phong_hoc_id)
            
            # Get teacher name
            gv_text = "Chưa phân công"
            if lhp.giang_vien and hasattr(lhp.giang_vien, 'id') and lhp.giang_vien.id:
                gv_text = lhp.giang_vien.id.ho_ten or "Chưa phân công"
            
            thu_text = self._get_thu_name(thu)
            tiet_text = f"{tiet_bat_dau} - {tiet_ket_thuc}" if tiet_bat_dau and tiet_ket_thuc else ""
            
            # Format like: "Thứ Hai, Tiết(1 - 3), P.A101, GV Name (01/01/2024 -> 01/06/2024)"
            formatted = f"{thu_text}, Tiết({tiet_text}), {phong_text}, {gv_text}"
            if ngay_bd_str or ngay_kt_str:
                formatted += f"\n({ngay_bd_str} -> {ngay_kt_str})"
            
            return formatted
            
        except Exception as e:
            logger.error(f"[TRA_CUU] Failed to format MongoDB session: {e}")
            return None
    
    def _format_date(self, date_val) -> str:
        """Format date to DD/MM/YYYY"""
        if not date_val:
            return ""
        
        try:
            if hasattr(date_val, 'strftime'):
                return date_val.strftime("%d/%m/%Y")
            else:
                from datetime import datetime
                dt = datetime.fromisoformat(str(date_val).replace('Z', '+00:00'))
                return dt.strftime("%d/%m/%Y")
        except Exception:
            return ""
    
    def _get_phong_name(self, phong_hoc_id: Optional[str]) -> str:
        """Get room name from ID"""
        if not phong_hoc_id:
            return "TBA"
        
        try:
            from infrastructure.persistence.models import Phong
            phong = Phong.objects.using('neon').filter(id=phong_hoc_id).first()
            if phong:
                return phong.ma_phong or phong.ten_phong or "TBA"
        except Exception as e:
            logger.error(f"[TRA_CUU] Failed to get phong name: {e}")
        
        return "TBA"
    
    def _get_thu_name(self, thu: int) -> str:
        """Map thu number to Vietnamese day name"""
        thu_map = {
            1: "Chủ Nhật",
            2: "Thứ Hai",
            3: "Thứ Ba",
            4: "Thứ Tư",
            5: "Thứ Năm",
            6: "Thứ Sáu",
            7: "Thứ Bảy",
            8: "Chủ Nhật",  # Alternative mapping for Sunday
        }
        return thu_map.get(thu, "N/A") if thu else "N/A"
