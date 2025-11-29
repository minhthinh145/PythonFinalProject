"""
Domain Layer - SinhVien Entity
Business logic for student domain
"""
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class SinhVienEntity:
    """
    SinhVien domain entity
    Combines Users and SinhVien model data
    """
    id: str
    ma_so_sinh_vien: str
    ho_ten: str
    khoa_id: str
    nganh_id: Optional[str] = None
    lop: Optional[str] = None
    khoa_hoc: Optional[str] = None
    ngay_nhap_hoc: Optional[date] = None
    
    # Additional fields from Users or related (Readonly/Joined)
    ten_khoa: Optional[str] = None
    ten_nganh: Optional[str] = None
    trang_thai_hoat_dong: Optional[bool] = None
    tai_khoan_id: Optional[str] = None
    email: Optional[str] = None # From Users
    
    def to_dict(self) -> dict:
        """
        Convert to dict for API response
        """
        return {
            'id': self.id,
            'maSoSinhVien': self.ma_so_sinh_vien,
            'hoTen': self.ho_ten,
            'khoaId': self.khoa_id,
            'nganhId': self.nganh_id,
            'lop': self.lop,
            'khoaHoc': self.khoa_hoc,
            'ngayNhapHoc': self.ngay_nhap_hoc.isoformat() if self.ngay_nhap_hoc else None,
            'tenKhoa': self.ten_khoa,
            'tenNganh': self.ten_nganh,
            'trangThaiHoatDong': self.trang_thai_hoat_dong,
            'taiKhoanId': self.tai_khoan_id,
            'email': self.email
        }
