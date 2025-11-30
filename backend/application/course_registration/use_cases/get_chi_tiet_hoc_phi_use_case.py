from typing import Dict, Any
from application.course_registration.interfaces.repositories import IHocPhiRepository
from core.types.service_result import ServiceResult

class GetChiTietHocPhiUseCase:
    def __init__(self, hoc_phi_repo: IHocPhiRepository):
        self.hoc_phi_repo = hoc_phi_repo

    def execute(self, sinh_vien_id: str, hoc_ky_id: str) -> ServiceResult[Dict[str, Any]]:
        try:
            hoc_phi = self.hoc_phi_repo.get_hoc_phi_by_sinh_vien(sinh_vien_id, hoc_ky_id)
            
            if not hoc_phi:
                return ServiceResult.fail(
                    message="Không tìm thấy thông tin học phí",
                    error_code="HOC_PHI_NOT_FOUND"
                )
            
            chi_tiet = []
            for item in hoc_phi.chi_tiet_hoc_phi_set.all():
                chi_tiet.append({
                    "maLop": item.lop_hoc_phan.ma_lop,
                    "tenMonHoc": item.lop_hoc_phan.hoc_phan.ten_hoc_phan,
                    "soTinChi": item.so_tin_chi,
                    "phiTinChi": float(item.phi_tin_chi),
                    "thanhTien": float(item.thanh_tien)
                })
                
            return ServiceResult.ok({
                "tongHocPhi": float(hoc_phi.tong_hoc_phi) if hoc_phi.tong_hoc_phi else 0,
                "trangThai": hoc_phi.trang_thai_thanh_toan,
                "soTinChi": hoc_phi.so_tin_chi if hasattr(hoc_phi, 'so_tin_chi') else 0, # Assuming model has this or calculated
                "chiTiet": chi_tiet
            })
        except Exception as e:
            return ServiceResult.fail(str(e))
