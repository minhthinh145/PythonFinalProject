from typing import List, Dict, Any
from application.enrollment.interfaces.repositories import IHocPhanRepository
from core.types.service_result import ServiceResult

class TraCuuHocPhanUseCase:
    def __init__(self, hoc_phan_repo: IHocPhanRepository):
        self.hoc_phan_repo = hoc_phan_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult[Dict[str, Any]]:
        try:
            hoc_phan_list = self.hoc_phan_repo.find_all_open(hoc_ky_id)
            
            data = []
            for hp in hoc_phan_list:
                data.append({
                    "id": str(hp.id),
                    "maHocPhan": hp.mon_hoc.ma_mon,
                    "tenHocPhan": hp.ten_hoc_phan,
                    "soTinChi": hp.mon_hoc.so_tin_chi,
                    "giangVien": "", # TODO: Get from LopHocPhan or DeXuat
                    "thoiKhoaBieu": "", # TODO: Get from LopHocPhan
                    "siSoToiDa": hp.so_lop * 50 if hp.so_lop else 0, # Estimate
                    "siSoHienTai": 0, # TODO: Count from GhiDanh
                    "trangThai": "Mở" if hp.trang_thai_mo else "Đóng"
                })
                
            return ServiceResult.ok({"hocPhan": data})
        except Exception as e:
            return ServiceResult.fail(str(e))
