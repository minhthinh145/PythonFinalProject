"""
Application Layer - Get Danh Sach Da Ghi Danh Use Case
"""
from core.types import ServiceResult
from application.enrollment.interfaces import IGhiDanhRepository

class GetDanhSachDaGhiDanhUseCase:
    """
    Use case to get list of enrolled subjects
    """
    
    def __init__(self, ghi_danh_repo: IGhiDanhRepository):
        self.ghi_danh_repo = ghi_danh_repo
        
    def execute(self, user_id: str) -> ServiceResult:
        """
        Execute logic
        """
        ghi_danh_list = self.ghi_danh_repo.find_by_sinh_vien(user_id)
        
        data = []
        for gd in ghi_danh_list:
            hoc_phan = gd.hoc_phan
            mon_hoc = hoc_phan.mon_hoc if hoc_phan else None
            
            de_xuat_list = mon_hoc.dexuathocphan_set.all() if mon_hoc and hasattr(mon_hoc, 'dexuathocphan_set') else []
            de_xuat = de_xuat_list[0] if de_xuat_list else None
            
            ten_giang_vien = None
            if de_xuat and de_xuat.giang_vien_de_xuat and de_xuat.giang_vien_de_xuat.id:
                ten_giang_vien = de_xuat.giang_vien_de_xuat.id.ho_ten
                
            data.append({
                'ghiDanhId': str(gd.id),
                'monHocId': str(hoc_phan.id) if hoc_phan else "",
                'maMonHoc': mon_hoc.ma_mon if mon_hoc else "",
                'tenMonHoc': mon_hoc.ten_mon if mon_hoc else "",
                'soTinChi': mon_hoc.so_tin_chi if mon_hoc else 0,
                'tenKhoa': mon_hoc.khoa.ten_khoa if mon_hoc and mon_hoc.khoa else "",
                'tenGiangVien': ten_giang_vien
            })
            
        return ServiceResult.ok(data, f"Lấy thành công {len(data)} môn học đã ghi danh")
