from typing import List, Dict, Any
from application.enrollment.interfaces.repositories import IHocPhanRepository
from core.types.service_result import ServiceResult

class TraCuuHocPhanUseCase:
    def __init__(self, hoc_phan_repo: IHocPhanRepository):
        self.hoc_phan_repo = hoc_phan_repo

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
            
            # Group by mon_hoc
            mon_hoc_map: Dict[str, Dict[str, Any]] = {}
            
            for lhp in lop_hoc_phans:
                mon_hoc = lhp.hoc_phan.mon_hoc if lhp.hoc_phan else None
                if not mon_hoc:
                    continue
                    
                mon_hoc_id = str(mon_hoc.id)
                
                if mon_hoc_id not in mon_hoc_map:
                    # Determine loaiMon
                    loai_mon = "dai_cuong"  # default
                    if hasattr(mon_hoc, 'loai_mon') and mon_hoc.loai_mon:
                        loai_mon = mon_hoc.loai_mon
                    elif hasattr(mon_hoc, 'loai') and mon_hoc.loai:
                        loai_mon = mon_hoc.loai
                    
                    mon_hoc_map[mon_hoc_id] = {
                        "maMon": mon_hoc.ma_mon or "",
                        "tenMon": mon_hoc.ten_mon or "",
                        "soTinChi": mon_hoc.so_tin_chi or 0,
                        "loaiMon": loai_mon,
                        "danhSachLop": []
                    }
                
                # Build TKB string from lich_hoc_dinh_ky
                tkb_lines = []
                # Correct related_name is lichhocdinhky_set
                lich_hocs = getattr(lhp, 'lichhocdinhky_set', None)
                if lich_hocs:
                    try:
                        for lh in lich_hocs.all():
                            thu = getattr(lh, 'thu', None) or ""
                            tiet_bat_dau = getattr(lh, 'tiet_bat_dau', None) or ""
                            tiet_ket_thuc = getattr(lh, 'tiet_ket_thuc', None) or ""
                            phong = getattr(lh, 'phong', None)  # FK is 'phong'
                            phong_ten = phong.ten_phong if phong else ""
                            tkb_lines.append(f"Thứ {thu}: Tiết {tiet_bat_dau}-{tiet_ket_thuc} ({phong_ten})")
                    except Exception:
                        pass
                
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
                    "thoiKhoaBieu": "\n".join(tkb_lines) if tkb_lines else "Chưa có TKB"
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
            return ServiceResult.fail(str(e))
