"""
Domain Layer - User Entity
Business logic for user domain
"""
from dataclasses import dataclass
from typing import Optional, Literal

# Map 1-1 với frontend Role type
Role = Literal["phong_dao_tao", "truong_khoa", "tro_ly_khoa", "giang_vien", "sinh_vien"]


@dataclass
class UserEntity:
    """
    User domain entity
    Map 1-1 với frontend User interface
    """
    id: str
    ho_ten: str              # hoTen
    loai_tai_khoan: Role     # loaiTaiKhoan
    ma_nhan_vien: Optional[str] = None  # maNhanVien
    mssv: Optional[str] = None          # mssv (mã số sinh viên)
    lop: Optional[str] = None           # lop
    nganh: Optional[str] = None         # nganh
    
    def is_student(self) -> bool:
        """Check if user is student"""
        return self.loai_tai_khoan == "sinh_vien"
    
    def is_lecturer(self) -> bool:
        """Check if user is lecturer"""
        return self.loai_tai_khoan == "giang_vien"
    
    def is_admin(self) -> bool:
        """Check if user is admin (phong dao tao)"""
        return self.loai_tai_khoan == "phong_dao_tao"
    
    def to_dict(self) -> dict:
        """
        Convert to dict for API response
        Map 1-1 frontend User interface (camelCase)
        """
        return {
            'id': self.id,
            'hoTen': self.ho_ten,
            'maNhanVien': self.ma_nhan_vien,
            'loaiTaiKhoan': self.loai_tai_khoan,
            'mssv': self.mssv,
            'lop': self.lop,
            'nganh': self.nganh,
        }
