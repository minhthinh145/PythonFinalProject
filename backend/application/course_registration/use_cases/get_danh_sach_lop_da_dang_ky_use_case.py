"""
Application Layer - Get Danh Sach Lop Da Dang Ky Use Case
"""
from typing import List, Dict, Any
from collections import defaultdict
from core.types import ServiceResult
from application.course_registration.interfaces import IDangKyHocPhanRepository

class GetDanhSachLopDaDangKyUseCase:
    """
    Use case to get list of registered course classes for student
    Returns grouped by MonHoc: MonHocInfoDTO[] with danhSachLop
    """
    
    def __init__(self, dang_ky_hp_repo: IDangKyHocPhanRepository):
        self.dang_ky_hp_repo = dang_ky_hp_repo
        
    def execute(self, sinh_vien_id: str, hoc_ky_id: str) -> ServiceResult:
        """
        Execute logic - returns MonHocInfoDTO[] grouped by môn học
        """
        try:
            # 1. Get registered classes
            dang_kys = self.dang_ky_hp_repo.find_by_sinh_vien_and_hoc_ky(sinh_vien_id, hoc_ky_id)
            
            # 2. Group by môn học
            mon_hoc_map: Dict[str, Dict] = {}
            
            for dk in dang_kys:
                lhp = dk.lop_hoc_phan
                mon_hoc = lhp.hoc_phan.mon_hoc
                ma_mon = mon_hoc.ma_mon
                
                # Initialize mon hoc entry if not exists
                if ma_mon not in mon_hoc_map:
                    mon_hoc_map[ma_mon] = {
                        "maMon": ma_mon,
                        "tenMon": mon_hoc.ten_mon,
                        "soTinChi": mon_hoc.so_tin_chi,
                        "danhSachLop": []
                    }
                
                # Build TKB list for this lớp
                tkb_list = []
                for lich in lhp.lichhocdinhky_set.all():
                    gv_text = lhp.giang_vien.id.ho_ten if lhp.giang_vien and lhp.giang_vien.id else "Chưa phân công"
                    thu_text = self._get_thu_name(lich.thu)
                    tiet_text = f"{lich.tiet_bat_dau} - {lich.tiet_ket_thuc}"
                    phong_text = lich.phong.ma_phong if lich.phong else "TBA"
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
                
                # Add lớp to môn học
                mon_hoc_map[ma_mon]["danhSachLop"].append({
                    "id": str(lhp.id),
                    "maLop": lhp.ma_lop,
                    "tenLop": lhp.ma_lop,
                    "soLuongHienTai": lhp.so_luong_hien_tai or 0,
                    "soLuongToiDa": lhp.so_luong_toi_da or 50,
                    "tkb": tkb_list
                })
            
            # 3. Convert to list
            result = list(mon_hoc_map.values())
            
            return ServiceResult.ok(result, "Lấy danh sách lớp đã đăng ký thành công")
            
        except Exception as e:
            print(f"Error getting lop da dang ky: {e}")
            return ServiceResult.fail("Lỗi khi lấy danh sách lớp đã đăng ký", error_code="INTERNAL_ERROR")

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
        return thu_map.get(thu, "N/A")
