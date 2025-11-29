"""
Application Layer - Get SinhVien Info DTOs
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class GetSinhVienInfoResponseDTO:
    """
    Response DTO for Get SinhVien Info
    Map 1-1 with frontend requirements
    """
    id: str
    maSoSinhVien: str
    hoTen: str
    khoaId: str
    nganhId: Optional[str]
    lop: Optional[str]
    khoaHoc: Optional[str]
    ngayNhapHoc: Optional[str]
    tenKhoa: Optional[str]
    tenNganh: Optional[str]
    email: Optional[str]
