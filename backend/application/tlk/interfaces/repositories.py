"""
Application Layer - TLK (Tro Ly Khoa) Repository Interfaces
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ============== DTOs ==============

@dataclass
class TLKMonHocDTO:
    """DTO for Mon Hoc in TLK's khoa"""
    id: str
    ma_mon: str
    ten_mon: str
    so_tin_chi: int


@dataclass
class TLKGiangVienDTO:
    """DTO for Giang Vien in TLK's khoa"""
    id: str
    ho_ten: str


@dataclass
class TLKPhongHocDTO:
    """DTO for Phong Hoc"""
    id: str
    ma_phong: str
    ten_co_so: Optional[str]
    suc_chua: Optional[int]


@dataclass
class TLKHocPhanForCreateLopDTO:
    """DTO for Hoc Phan available to create Lop"""
    id: str
    ma_hoc_phan: str
    ten_hoc_phan: str
    so_tin_chi: int
    so_sinh_vien_ghi_danh: int
    ten_giang_vien: Optional[str]
    giang_vien_id: Optional[str]


@dataclass
class TLKDeXuatHocPhanDTO:
    """DTO for De Xuat Hoc Phan of TLK"""
    id: str
    ma_hoc_phan: str
    ten_hoc_phan: str
    so_tin_chi: int
    giang_vien: Optional[str]
    trang_thai: str


# ============== Interfaces ==============

class ITLKRepository(ABC):
    """Repository interface for TLK operations"""

    @abstractmethod
    def get_khoa_id_by_user(self, user_id: str) -> Optional[str]:
        """
        Get khoa_id from TLK user
        """
        pass

    @abstractmethod
    def get_mon_hoc_by_khoa(self, khoa_id: str) -> List[TLKMonHocDTO]:
        """
        Get all Mon Hoc belonging to a Khoa
        """
        pass

    @abstractmethod
    def get_giang_vien_by_khoa(self, khoa_id: str) -> List[TLKGiangVienDTO]:
        """
        Get all Giang Vien belonging to a Khoa
        """
        pass

    @abstractmethod
    def get_phong_hoc_by_khoa(self, khoa_id: str) -> List[TLKPhongHocDTO]:
        """
        Get all Phong Hoc associated with TLK's khoa
        """
        pass

    @abstractmethod
    def get_available_phong_hoc(self, khoa_id: str) -> List[TLKPhongHocDTO]:
        """
        Get available (unassigned) Phong Hoc
        """
        pass


class ITLKHocPhanRepository(ABC):
    """Repository interface for TLK HocPhan/LopHocPhan operations"""

    @abstractmethod
    def get_hoc_phans_for_create_lop(
        self, 
        hoc_ky_id: str, 
        khoa_id: str
    ) -> List[TLKHocPhanForCreateLopDTO]:
        """
        Get Hoc Phans that have been approved for creating Lop Hoc Phan
        """
        pass


class ITLKDeXuatRepository(ABC):
    """Repository interface for TLK De Xuat Hoc Phan operations"""

    @abstractmethod
    def get_de_xuat_by_khoa(
        self, 
        khoa_id: str, 
        hoc_ky_id: Optional[str] = None
    ) -> List[TLKDeXuatHocPhanDTO]:
        """
        Get De Xuat Hoc Phan created by TLK of a Khoa
        """
        pass

    @abstractmethod
    def create_de_xuat(
        self,
        khoa_id: str,
        nguoi_tao_id: str,
        hoc_ky_id: str,
        mon_hoc_id: str,
        so_lop_du_kien: int,
        giang_vien_id: Optional[str] = None
    ) -> bool:
        """
        Create a new De Xuat Hoc Phan
        """
        pass
