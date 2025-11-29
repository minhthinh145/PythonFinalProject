from typing import List, Dict, Any
from application.enrollment.interfaces import IHocKyRepository
from core.types.service_result import ServiceResult

class GetHocKyUseCase:
    def __init__(self, hoc_ky_repo: IHocKyRepository):
        self.hoc_ky_repo = hoc_ky_repo

    def execute(self) -> ServiceResult[List[Dict[str, Any]]]:
        try:
            hoc_ky_list = self.hoc_ky_repo.get_all_hoc_ky()
            
            data = []
            for hk in hoc_ky_list:
                data.append({
                    'id': str(hk.id),
                    'tenHocKy': hk.ten_hoc_ky,
                    'namHoc': hk.id_nien_khoa.ten_nien_khoa,
                    'hocKy': hk.ma_hoc_ky
                })
                
            return ServiceResult.ok(data)
        except Exception as e:
            return ServiceResult.fail(str(e))
