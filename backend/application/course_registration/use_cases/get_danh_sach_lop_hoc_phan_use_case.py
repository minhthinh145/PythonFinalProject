"""
Application Layer - Get Danh Sach Lop Hoc Phan Use Case
"""
from typing import List, Dict, Any, Optional
from core.types import ServiceResult
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository
)
from infrastructure.persistence.mongodb_service import get_mongodb_service
import logging

logger = logging.getLogger(__name__)


class GetDanhSachLopHocPhanUseCase:
    """
    Use case to get list of available course classes for student
    
    TKB data flow:
    - TKB is stored in MongoDB collection 'thoi_khoa_bieu_mon_hoc'
    - Each document has: maHocPhan, hocKyId, danhSachLop[]
    - We need to match MongoDB TKB with PostgreSQL LopHocPhan by tenLop
    """
    
    def __init__(
        self,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        dang_ky_hp_repo: IDangKyHocPhanRepository
    ):
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.dang_ky_hp_repo = dang_ky_hp_repo
        self.mongo_service = get_mongodb_service()
        
    def execute(self, sinh_vien_id: str, hoc_ky_id: str) -> ServiceResult:
        """
        Execute logic
        """
        try:
            # 1. Get registered class IDs
            registered_ids = set(self.dang_ky_hp_repo.find_registered_class_ids(sinh_vien_id, hoc_ky_id))
            
            # 2. Get all classes for semester from PostgreSQL
            all_classes = self.lop_hoc_phan_repo.find_all_by_hoc_ky(hoc_ky_id)
            
            # 3. Get all TKB from MongoDB for this semester
            mongo_tkb_map = self._build_mongo_tkb_map(hoc_ky_id)
            
            # 4. Group by MonHoc
            mon_hoc_map: Dict[str, Any] = {}
            
            for lhp in all_classes:
                # Skip if registered
                if str(lhp.id) in registered_ids:
                    continue
                    
                mon_hoc = lhp.hoc_phan.mon_hoc
                ma_mon = mon_hoc.ma_mon
                
                if ma_mon not in mon_hoc_map:
                    mon_hoc_map[ma_mon] = {
                        "monHocId": str(mon_hoc.id),
                        "maMon": ma_mon,
                        "tenMon": mon_hoc.ten_mon,
                        "soTinChi": mon_hoc.so_tin_chi,
                        "laMonChung": mon_hoc.la_mon_chung,
                        "loaiMon": mon_hoc.loai_mon,
                        "danhSachLop": []
                    }
                
                # Get TKB from MongoDB (primary source)
                tkb_list = self._get_tkb_for_lop(ma_mon, lhp.ma_lop, mongo_tkb_map, lhp)
                
                mon_hoc_map[ma_mon]["danhSachLop"].append({
                    "id": str(lhp.id),
                    "maLop": lhp.ma_lop,
                    "tenLop": lhp.ma_lop,
                    "soLuongHienTai": lhp.so_luong_hien_tai or 0,
                    "soLuongToiDa": lhp.so_luong_toi_da or 50,
                    "tkb": tkb_list
                })
            
            # 5. Categorize
            mon_chung = []
            bat_buoc = []
            tu_chon = []
            
            for dto in mon_hoc_map.values():
                # Clean up internal fields
                la_mon_chung = dto.pop("laMonChung", False)
                loai_mon = dto.pop("loaiMon", "")
                
                if la_mon_chung:
                    mon_chung.append(dto)
                elif loai_mon == "chuyen_nganh":
                    bat_buoc.append(dto)
                else:
                    tu_chon.append(dto)
                    
            return ServiceResult.ok({
                "monChung": mon_chung,
                "batBuoc": bat_buoc,
                "tuChon": tu_chon
            }, "Lấy danh sách lớp học phần thành công")
            
        except Exception as e:
            logger.error(f"Error getting danh sach lop: {e}")
            import traceback
            traceback.print_exc()
            return ServiceResult.fail("Lỗi khi lấy danh sách lớp học phần", error_code="INTERNAL_ERROR")
    
    def _build_mongo_tkb_map(self, hoc_ky_id: str) -> Dict[str, Dict]:
        """
        Build a map of maHocPhan -> { tenLop -> tkb_info }
        from MongoDB thoi_khoa_bieu_mon_hoc collection
        
        Note: MongoDB data can have both camelCase or snake_case fields
        """
        tkb_map = {}
        
        if not self.mongo_service.is_available:
            logger.warning("MongoDB not available, TKB will be empty")
            return tkb_map
        
        try:
            # Get all TKB for this semester
            all_tkb = self.mongo_service.get_tkb_by_hoc_ky(hoc_ky_id)
            
            for tkb_doc in all_tkb:
                ma_hoc_phan = tkb_doc.get('ma_hoc_phan')
                danh_sach_lop = tkb_doc.get('danhSachLop', [])
                
                if ma_hoc_phan not in tkb_map:
                    tkb_map[ma_hoc_phan] = {}
                
                for lop in danh_sach_lop:
                    # Support both camelCase and snake_case
                    ten_lop = lop.get('tenLop') or lop.get('ten_lop')
                    if ten_lop:
                        # Normalize to a consistent format
                        tkb_map[ma_hoc_phan][ten_lop] = self._normalize_lop_data(lop)
            
            logger.debug(f"Built TKB map with {len(tkb_map)} môn học")
            
        except Exception as e:
            logger.error(f"Failed to build TKB map: {e}")
        
        return tkb_map
    
    def _normalize_lop_data(self, lop: Dict) -> Dict:
        """
        Normalize lop data to consistent format (camelCase)
        Handles both snake_case and camelCase from MongoDB
        """
        return {
            'tenLop': lop.get('tenLop') or lop.get('ten_lop'),
            'phongHocId': lop.get('phongHocId') or lop.get('phong_hoc_id'),
            'ngayBatDau': lop.get('ngayBatDau') or lop.get('ngay_bat_dau'),
            'ngayKetThuc': lop.get('ngayKetThuc') or lop.get('ngay_ket_thuc'),
            'tietBatDau': lop.get('tietBatDau') or lop.get('tiet_bat_dau'),
            'tietKetThuc': lop.get('tietKetThuc') or lop.get('tiet_ket_thuc'),
            'thuTrongTuan': lop.get('thuTrongTuan') or lop.get('thu_trong_tuan'),
        }
    
    def _get_tkb_for_lop(
        self, 
        ma_mon: str, 
        ten_lop: str, 
        mongo_tkb_map: Dict, 
        lhp: Any
    ) -> List[Dict]:
        """
        Get TKB info for a specific class
        Priority: MongoDB > PostgreSQL fallback
        """
        tkb_list = []
        
        # Try MongoDB first
        mongo_lop = mongo_tkb_map.get(ma_mon, {}).get(ten_lop)
        
        if mongo_lop:
            # Found in MongoDB - use this data
            tkb_info = self._format_mongo_tkb(mongo_lop, lhp)
            if tkb_info:
                tkb_list.append(tkb_info)
        else:
            # Fallback to PostgreSQL if no MongoDB data
            tkb_list = self._get_tkb_from_postgres(lhp)
        
        return tkb_list
    
    def _format_mongo_tkb(self, mongo_lop: Dict, lhp: Any) -> Optional[Dict]:
        """
        Format MongoDB TKB data to match FE expectations
        
        MongoDB fields:
        - tenLop, phongHocId, ngayBatDau, ngayKetThuc, tietBatDau, tietKetThuc, thuTrongTuan
        """
        try:
            thu = mongo_lop.get('thuTrongTuan')
            tiet_bat_dau = mongo_lop.get('tietBatDau')
            tiet_ket_thuc = mongo_lop.get('tietKetThuc')
            phong_hoc_id = mongo_lop.get('phongHocId')
            
            # Get dates
            ngay_bd = mongo_lop.get('ngayBatDau')
            ngay_kt = mongo_lop.get('ngayKetThuc')
            
            # Format dates
            if ngay_bd:
                if hasattr(ngay_bd, 'strftime'):
                    ngay_bd_str = ngay_bd.strftime("%d/%m/%Y")
                else:
                    from datetime import datetime
                    ngay_bd_dt = datetime.fromisoformat(str(ngay_bd).replace('Z', '+00:00'))
                    ngay_bd_str = ngay_bd_dt.strftime("%d/%m/%Y")
            else:
                ngay_bd_str = ""
            
            if ngay_kt:
                if hasattr(ngay_kt, 'strftime'):
                    ngay_kt_str = ngay_kt.strftime("%d/%m/%Y")
                else:
                    from datetime import datetime
                    ngay_kt_dt = datetime.fromisoformat(str(ngay_kt).replace('Z', '+00:00'))
                    ngay_kt_str = ngay_kt_dt.strftime("%d/%m/%Y")
            else:
                ngay_kt_str = ""
            
            # Get room name
            phong_text = self._get_phong_name(phong_hoc_id)
            
            # Get teacher name
            gv_text = "Chưa phân công"
            if lhp.giang_vien and lhp.giang_vien.id:
                gv_text = lhp.giang_vien.id.ho_ten
            
            thu_text = self._get_thu_name(thu)
            tiet_text = f"{tiet_bat_dau} - {tiet_ket_thuc}" if tiet_bat_dau and tiet_ket_thuc else ""
            
            formatted = f"{thu_text}, Tiết({tiet_text}), {phong_text}, {gv_text}\n({ngay_bd_str} -> {ngay_kt_str})"
            
            return {
                "thu": thu,
                "tiet": tiet_text,
                "phong": phong_text,
                "giangVien": gv_text,
                "ngayBatDau": ngay_bd_str,
                "ngayKetThuc": ngay_kt_str,
                "formatted": formatted
            }
            
        except Exception as e:
            logger.error(f"Failed to format MongoDB TKB: {e}")
            return None
    
    def _get_phong_name(self, phong_hoc_id: Optional[str]) -> str:
        """Get room name from ID"""
        if not phong_hoc_id:
            return "TBA"
        
        try:
            from core.models import Phong
            phong = Phong.objects.filter(id=phong_hoc_id).first()
            if phong:
                return phong.ma_phong
        except Exception:
            pass
        
        return "TBA"
    
    def _get_tkb_from_postgres(self, lhp: Any) -> List[Dict]:
        """
        Fallback: Get TKB from PostgreSQL lich_hoc_dinh_ky
        Used when MongoDB is not available or has no data
        """
        tkb_list = []
        
        try:
            for lich in lhp.lichhocdinhky_set.all():
                thu_text = self._get_thu_name(lich.thu)
                tiet_text = f"{lich.tiet_bat_dau} - {lich.tiet_ket_thuc}"
                phong_text = lich.phong.ma_phong if lich.phong else "TBA"
                gv_text = lhp.giang_vien.id.ho_ten if lhp.giang_vien and lhp.giang_vien.id else "Chưa phân công"
                ngay_bd = lhp.ngay_bat_dau.strftime("%d/%m/%Y") if lhp.ngay_bat_dau else ""
                ngay_kt = lhp.ngay_ket_thuc.strftime("%d/%m/%Y") if lhp.ngay_ket_thuc else ""
                
                tkb_list.append({
                    "thu": lich.thu,
                    "tiet": tiet_text,
                    "phong": phong_text,
                    "giangVien": gv_text,
                    "ngayBatDau": ngay_bd,
                    "ngayKetThuc": ngay_kt,
                    "formatted": f"{thu_text}, Tiết({tiet_text}), {phong_text}, {gv_text}\n({ngay_bd} -> {ngay_kt})"
                })
        except Exception as e:
            logger.error(f"Failed to get TKB from PostgreSQL: {e}")
        
        return tkb_list

    def _get_thu_name(self, thu: int) -> str:
        thu_map = {
            1: "Chủ Nhật",
            2: "Thứ Hai",
            3: "Thứ Ba",
            4: "Thứ Tư",
            5: "Thứ Năm",
            6: "Thứ Sáu",
            7: "Thứ Bảy",
        }
        return thu_map.get(thu, "N/A") if thu else "N/A"
