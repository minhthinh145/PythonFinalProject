"""
Application Layer - TK Interfaces
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dataclasses import dataclass


@dataclass
class DeXuatHocPhanForTKDTO:
    """DTO for De Xuat Hoc Phan - used by TK views"""
    id: str
    ma_hoc_phan: str
    ten_hoc_phan: str
    so_tin_chi: int
    giang_vien: str
    trang_thai: str


class ITruongKhoaRepository(ABC):
    """Interface for Truong Khoa Repository"""
    
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[Any]:
        """Find truong khoa by user_id"""
        pass
    
    @abstractmethod
    def get_khoa_id(self, user_id: str) -> Optional[str]:
        """Get khoa_id for truong khoa"""
        pass


class IDeXuatHocPhanRepository(ABC):
    """Interface for De Xuat Hoc Phan Repository (for TK operations)"""
    
    @abstractmethod
    def find_by_id(self, de_xuat_id: str) -> Optional[Any]:
        """Find de xuat by ID"""
        pass
    
    @abstractmethod
    def find_by_khoa_and_status(
        self, 
        khoa_id: str, 
        trang_thai: str,
        hoc_ky_id: Optional[str] = None
    ) -> List[Any]:
        """Find de xuat by khoa and status"""
        pass
    
    @abstractmethod
    def update_trang_thai(
        self, 
        de_xuat_id: str, 
        trang_thai: str,
        nguoi_duyet_id: str
    ) -> bool:
        """Update trang thai"""
        pass
    
    @abstractmethod
    def reject(
        self, 
        de_xuat_id: str, 
        nguoi_tu_choi_id: str
    ) -> bool:
        """Reject de xuat"""
        pass
