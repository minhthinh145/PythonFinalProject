"""
Application Layer - Common Interfaces (Ports)

Repository interfaces for common/shared domain entities
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from infrastructure.persistence.models import HocKy, NienKhoa, NganhHoc as Nganh


class IHocKyRepository(ABC):
    """Interface for HocKy repository"""
    
    @abstractmethod
    def find_hien_hanh(self) -> Optional[HocKy]:
        """Find the current active semester"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[HocKy]:
        """Find semester by ID"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[HocKy]:
        """Get all semesters with nien khoa"""
        pass


class INienKhoaRepository(ABC):
    """Interface for NienKhoa repository"""
    
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[NienKhoa]:
        """Find academic year by ID"""
        pass


class INganhRepository(ABC):
    """Interface for Nganh (major/program) repository"""
    
    @abstractmethod
    def find_all(self, khoa_id: Optional[str] = None) -> List[Nganh]:
        """
        Find all programs, optionally filtered by faculty
        
        Args:
            khoa_id: Optional faculty ID to filter
        """
        pass
    
    @abstractmethod
    def find_without_policy(self, hoc_ky_id: str, khoa_id: str) -> List[Nganh]:
        """
        Find programs without tuition policy for given semester and faculty
        
        Args:
            hoc_ky_id: Semester ID  
            khoa_id: Faculty ID
        """
        pass
