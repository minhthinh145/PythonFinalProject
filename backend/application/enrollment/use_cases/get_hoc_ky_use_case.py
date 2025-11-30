from typing import List, Dict, Any
from application.enrollment.interfaces import IHocKyRepository
from core.types.service_result import ServiceResult

class GetHocKyUseCase:
    def __init__(self, hoc_ky_repo: IHocKyRepository):
        self.hoc_ky_repo = hoc_ky_repo

    def execute(self) -> ServiceResult[List[Dict[str, Any]]]:
        try:
            hoc_ky_list = self.hoc_ky_repo.get_all_hoc_ky()
            
            # Group by NienKhoa
            nien_khoa_map = {}
            for hk in hoc_ky_list:
                nk_id = str(hk.id_nien_khoa.id)
                if nk_id not in nien_khoa_map:
                    nien_khoa_map[nk_id] = {
                        'nienKhoaId': nk_id,
                        'tenNienKhoa': hk.id_nien_khoa.ten_nien_khoa,
                        'hocKy': []
                    }
                
                nien_khoa_map[nk_id]['hocKy'].append({
                    'id': str(hk.id),
                    'tenHocKy': hk.ten_hoc_ky,
                    'maHocKy': hk.ma_hoc_ky,
                    'ngayBatDau': hk.ngay_bat_dau,
                    'ngayKetThuc': hk.ngay_ket_thuc
                })
            
            data = list(nien_khoa_map.values())
            return ServiceResult.ok(data)
        except Exception as e:
            return ServiceResult.fail(str(e))
