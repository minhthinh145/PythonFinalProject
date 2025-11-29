"""
Application Layer - Get Mon Hoc Ghi Danh Use Case
"""
from typing import Optional
from core.types import ServiceResult
from application.enrollment.interfaces import (
    IHocKyRepository,
    IHocPhanRepository
)

class GetMonHocGhiDanhUseCase:
    """
    Use case to get list of subjects available for enrollment
    """
    
    def __init__(
        self,
        hoc_ky_repo: IHocKyRepository,
        hoc_phan_repo: IHocPhanRepository
    ):
        self.hoc_ky_repo = hoc_ky_repo
        self.hoc_phan_repo = hoc_phan_repo
        
    def execute(self, hoc_ky_id: Optional[str] = None) -> ServiceResult:
        """
        Execute logic
        """
        target_hoc_ky_id = hoc_ky_id
        
        if not target_hoc_ky_id:
            hoc_ky_hien_hanh = self.hoc_ky_repo.get_current_hoc_ky()
            if not hoc_ky_hien_hanh:
                return ServiceResult.fail(
                    "Không có học kỳ hiện hành", 
                    error_code="HOC_KY_HIEN_HANH_NOT_FOUND"
                )
            target_hoc_ky_id = hoc_ky_hien_hanh.id
            
        # Get open subjects
        hoc_phan_list = self.hoc_phan_repo.find_all_open(target_hoc_ky_id)
        
        # Map to DTO
        data = []
        for hp in hoc_phan_list:
            # Handle relationship access safely (assuming Django models or similar objects)
            mon_hoc = hp.mon_hoc
            de_xuat_list = mon_hoc.dexuathocphan_set.all() if hasattr(mon_hoc, 'dexuathocphan_set') else []
            de_xuat = de_xuat_list[0] if de_xuat_list else None
            
            ten_giang_vien = "Chưa có giảng viên"
            if de_xuat and de_xuat.giang_vien_de_xuat and de_xuat.giang_vien_de_xuat.id:
                ten_giang_vien = de_xuat.giang_vien_de_xuat.id.ho_ten
                
            data.append({
                'id': str(hp.id),
                'maMonHoc': mon_hoc.ma_mon if mon_hoc else "",
                'tenMonHoc': mon_hoc.ten_mon if mon_hoc else "",
                'soTinChi': mon_hoc.so_tin_chi if mon_hoc else 0,
                'tenKhoa': mon_hoc.khoa.ten_khoa if mon_hoc and mon_hoc.khoa else "",
                'tenGiangVien': ten_giang_vien
            })
            
        return ServiceResult.ok(data, "Lấy danh sách môn học ghi danh thành công")
