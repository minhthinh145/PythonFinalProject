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
            
            # Calculate totals
            chi_tiet = []
            tong_tin_chi = 0
            don_gia = 0
            
            for item in hoc_phi.chitiethocphi_set.all():
                # Skip if lop_hoc_phan doesn't exist (deleted or invalid reference)
                try:
                    lop_hoc_phan = item.lop_hoc_phan
                    if not lop_hoc_phan:
                        continue
                    mon_hoc = lop_hoc_phan.hoc_phan.mon_hoc
                except Exception:
                    # Skip invalid ChiTietHocPhi
                    continue
                
                tong_tin_chi += item.so_tin_chi
                don_gia = float(item.phi_tin_chi)  # Same for all
                
                chi_tiet.append({
                    "maMon": mon_hoc.ma_mon,
                    "tenMon": mon_hoc.ten_mon,
                    "maLop": lop_hoc_phan.ma_lop,
                    "soTinChi": item.so_tin_chi,
                    "donGia": float(item.phi_tin_chi),
                    "thanhTien": float(item.thanh_tien)
                })
            
            # Build chinhSach from policy
            chinh_sach = None
            if hoc_phi.chinh_sach:
                chinh_sach = {
                    "tenChinhSach": f"Chính sách học phí {hoc_phi.hoc_ky.ten_hoc_ky}" if hoc_phi.hoc_ky else "Chính sách học phí",
                    "ngayHieuLuc": hoc_phi.chinh_sach.ngay_hieu_luc.isoformat() if hoc_phi.chinh_sach.ngay_hieu_luc else "",
                    "ngayHetHieuLuc": hoc_phi.chinh_sach.ngay_het_hieu_luc.isoformat() if hoc_phi.chinh_sach.ngay_het_hieu_luc else ""
                }
            else:
                chinh_sach = {
                    "tenChinhSach": "Chính sách học phí mặc định",
                    "ngayHieuLuc": "",
                    "ngayHetHieuLuc": ""
                }
                
            return ServiceResult.ok({
                "tongHocPhi": float(hoc_phi.tong_hoc_phi) if hoc_phi.tong_hoc_phi else 0,
                "soTinChiDangKy": tong_tin_chi,
                "donGiaTinChi": don_gia,
                "chinhSach": chinh_sach,
                "chiTiet": chi_tiet,
                "trangThaiThanhToan": hoc_phi.trang_thai_thanh_toan or "chua_thanh_toan"
            })
        except Exception as e:
            print(f"Error getting hoc phi: {e}")
            return ServiceResult.fail(str(e))
