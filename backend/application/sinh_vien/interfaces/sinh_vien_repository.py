"""
Domain Layer - SinhVien Repository Interface
"""
from abc import ABC, abstractmethod
from typing import Optional
from domain.sinh_vien.entities import SinhVienEntity

class ISinhVienRepository(ABC):
    """
    Interface for SinhVien repository
    """
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[SinhVienEntity]:
        """Get student by ID"""
        pass
        
    @abstractmethod
    def get_by_mssv(self, mssv: str) -> Optional[SinhVienEntity]:
        """Get student by MSSV"""
        pass
