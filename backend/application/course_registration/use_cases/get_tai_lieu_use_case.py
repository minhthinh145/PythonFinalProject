"""
Get Tai Lieu By Lop Hoc Phan Use Case
"""
import os
from typing import List, Dict, Any
from core.types import ServiceResult


class GetTaiLieuByLopHocPhanUseCase:
    """
    Gets all documents for a class
    """
    
    def __init__(self, tai_lieu_repo, dang_ky_repo=None):
        self.tai_lieu_repo = tai_lieu_repo
        self.dang_ky_repo = dang_ky_repo
    
    def execute(self, sinh_vien_id: str, lop_hoc_phan_id: str) -> ServiceResult[List[Dict[str, Any]]]:
        try:
            # Check if student is registered for this class
            if self.dang_ky_repo:
                is_registered = self.dang_ky_repo.is_student_registered(sinh_vien_id, lop_hoc_phan_id)
                if not is_registered:
                    return ServiceResult.fail(
                        message="Bạn chưa đăng ký lớp học phần này hoặc đã hủy đăng ký",
                        error_code="NOT_REGISTERED"
                    )
            
            tai_lieus = self.tai_lieu_repo.find_by_lop_hoc_phan(lop_hoc_phan_id)
            
            s3_base_url = os.getenv("AWS_S3_BASE_URL", "https://hcmue-tailieu-hoctap-20251029.s3.ap-southeast-2.amazonaws.com")
            
            result = []
            for tl in tai_lieus:
                result.append({
                    "id": str(tl.id),
                    "tenTaiLieu": tl.ten_tai_lieu,
                    "fileType": tl.file_type or "",
                    "fileUrl": f"{s3_base_url}/{tl.file_path}" if tl.file_path else "",
                    "uploadedAt": tl.created_at.isoformat() if tl.created_at else "",
                    "uploadedBy": tl.uploaded_by.ho_ten if tl.uploaded_by else "Giảng viên"
                })
            
            return ServiceResult.ok(result, "Lấy danh sách tài liệu thành công")
            
        except Exception as e:
            print(f"Error getting tai lieu: {e}")
            return ServiceResult.fail(str(e), error_code="INTERNAL_ERROR")


class GetLopDaDangKyWithTaiLieuUseCase:
    """
    Gets all registered classes with their documents for a student
    """
    
    def __init__(self, dang_ky_repo, tai_lieu_repo):
        self.dang_ky_repo = dang_ky_repo
        self.tai_lieu_repo = tai_lieu_repo
    
    def execute(self, sinh_vien_id: str, hoc_ky_id: str) -> ServiceResult[List[Dict[str, Any]]]:
        try:
            # 1. Get registered classes
            dang_kys = self.dang_ky_repo.find_by_sinh_vien_and_hoc_ky(sinh_vien_id, hoc_ky_id)
            
            s3_base_url = os.getenv("AWS_S3_BASE_URL", "https://hcmue-tailieu-hoctap-20251029.s3.ap-southeast-2.amazonaws.com")
            
            result = []
            for dk in dang_kys:
                lhp = dk.lop_hoc_phan
                mon_hoc = lhp.hoc_phan.mon_hoc
                
                # Get tai lieu for this class
                tai_lieus = self.tai_lieu_repo.find_by_lop_hoc_phan(str(lhp.id))
                tai_lieu_list = []
                for tl in tai_lieus:
                    tai_lieu_list.append({
                        "id": str(tl.id),
                        "tenTaiLieu": tl.ten_tai_lieu,
                        "fileType": tl.file_type or "",
                        "fileUrl": f"{s3_base_url}/{tl.file_path}" if tl.file_path else "",
                        "uploadedAt": tl.created_at.isoformat() if tl.created_at else "",
                        "uploadedBy": tl.uploaded_by.ho_ten if tl.uploaded_by else "Giảng viên"
                    })
                
                gv_text = lhp.giang_vien.id.ho_ten if lhp.giang_vien and lhp.giang_vien.id else "Chưa phân công"
                
                result.append({
                    "lopHocPhanId": str(lhp.id),
                    "maLop": lhp.ma_lop,
                    "maMon": mon_hoc.ma_mon,
                    "tenMon": mon_hoc.ten_mon,
                    "soTinChi": mon_hoc.so_tin_chi,
                    "giangVien": gv_text,
                    "trangThaiDangKy": dk.trang_thai or "da_dang_ky",
                    "ngayDangKy": dk.ngay_dang_ky.isoformat() if hasattr(dk, 'ngay_dang_ky') and dk.ngay_dang_ky else "",
                    "taiLieu": tai_lieu_list
                })
            
            return ServiceResult.ok(result, "Lấy danh sách lớp đã đăng ký với tài liệu thành công")
            
        except Exception as e:
            print(f"Error getting lop da dang ky with tai lieu: {e}")
            return ServiceResult.fail(str(e), error_code="INTERNAL_ERROR")
