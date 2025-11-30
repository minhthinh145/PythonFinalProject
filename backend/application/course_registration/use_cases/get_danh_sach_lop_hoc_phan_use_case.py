"""
Application Layer - Get Danh Sach Lop Hoc Phan Use Case
"""
from typing import List, Dict, Any
from core.types import ServiceResult
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository
)

class GetDanhSachLopHocPhanUseCase:
    """
    Use case to get list of available course classes for student
    """
    
    def __init__(
        self,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        dang_ky_hp_repo: IDangKyHocPhanRepository
    ):
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.dang_ky_hp_repo = dang_ky_hp_repo
        
    def execute(self, sinh_vien_id: str, hoc_ky_id: str) -> ServiceResult:
        """
        Execute logic
        """
        try:
            # 1. Get registered class IDs
            registered_ids = set(self.dang_ky_hp_repo.find_registered_class_ids(sinh_vien_id, hoc_ky_id))
            
            # 2. Get all classes for semester
            all_classes = self.lop_hoc_phan_repo.find_all_by_hoc_ky(hoc_ky_id)
            
            # 3. Group by MonHoc
            mon_hoc_map: Dict[str, Any] = {}
            
            for lhp in all_classes:
                # Skip if registered
                if str(lhp.id) in registered_ids:
                    continue
                    
                mon_hoc = lhp.hoc_phan.mon_hoc
                ma_mon = mon_hoc.ma_mon
                
                if ma_mon not in mon_hoc_map:
                    mon_hoc_map[ma_mon] = {
                        "maMon": ma_mon,
                        "tenMon": mon_hoc.ten_mon,
                        "soTinChi": mon_hoc.so_tin_chi,
                        "laMonChung": mon_hoc.la_mon_chung,
                        "loaiMon": mon_hoc.loai_mon,
                        "danhSachLop": []
                    }
                
                # Format TKB
                tkb_list = []
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
                
                mon_hoc_map[ma_mon]["danhSachLop"].append({
                    "id": str(lhp.id),
                    "maLop": lhp.ma_lop,
                    "tenLop": lhp.ma_lop,
                    "soLuongHienTai": lhp.so_luong_hien_tai or 0,
                    "soLuongToiDa": lhp.so_luong_toi_da or 50,
                    "tkb": tkb_list
                })
            
            # 4. Categorize
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
            print(f"Error getting danh sach lop: {e}")
            return ServiceResult.fail("Lỗi khi lấy danh sách lớp học phần", error_code="INTERNAL_ERROR")

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
