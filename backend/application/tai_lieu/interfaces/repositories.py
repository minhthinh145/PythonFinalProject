"""
Application Layer - TaiLieu Repository Interfaces

Contracts for infrastructure layer implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


# ============== DTOs ==============

@dataclass
class TaiLieuDTO:
    """DTO for TaiLieu - matches frontend GVDocumentDTO and SVTaiLieuDTO"""
    id: str
    ten_tai_lieu: str
    file_path: str
    file_type: str
    created_at: Optional[str]
    uploaded_by_id: Optional[str]
    uploaded_by_name: Optional[str]


@dataclass 
class CreateTaiLieuDTO:
    """DTO for creating TaiLieu"""
    lop_hoc_phan_id: str
    ten_tai_lieu: str
    file_path: str
    file_type: str
    uploaded_by: str


# ============== Interfaces ==============

class ITaiLieuRepository(ABC):
    """Repository interface for TaiLieu (Documents) operations"""

    @abstractmethod
    def find_by_lop_hoc_phan(self, lop_hoc_phan_id: str) -> List[TaiLieuDTO]:
        """
        Get all TaiLieu for a LopHocPhan
        
        Args:
            lop_hoc_phan_id: UUID of LopHocPhan
            
        Returns:
            List of TaiLieuDTO
        """
        pass

    @abstractmethod
    def find_by_id(self, tai_lieu_id: str) -> Optional[TaiLieuDTO]:
        """
        Get TaiLieu by ID
        
        Args:
            tai_lieu_id: UUID of TaiLieu
            
        Returns:
            TaiLieuDTO or None if not found
        """
        pass

    @abstractmethod
    def create(self, data: CreateTaiLieuDTO) -> TaiLieuDTO:
        """
        Create a new TaiLieu record
        
        Args:
            data: CreateTaiLieuDTO with all required fields
            
        Returns:
            Created TaiLieuDTO
        """
        pass

    @abstractmethod
    def delete(self, tai_lieu_id: str) -> bool:
        """
        Delete TaiLieu by ID
        
        Args:
            tai_lieu_id: UUID of TaiLieu
            
        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def update_name(self, tai_lieu_id: str, new_name: str) -> Optional[TaiLieuDTO]:
        """
        Update TaiLieu name
        
        Args:
            tai_lieu_id: UUID of TaiLieu
            new_name: New name for the document
            
        Returns:
            Updated TaiLieuDTO or None if not found
        """
        pass

    @abstractmethod
    def get_lop_hoc_phan_owner(self, lop_hoc_phan_id: str) -> Optional[str]:
        """
        Get the GiangVien user_id who owns this LopHocPhan
        
        Args:
            lop_hoc_phan_id: UUID of LopHocPhan
            
        Returns:
            UUID of GiangVien's user account or None if not found
        """
        pass

    @abstractmethod
    def is_student_enrolled(self, lop_hoc_phan_id: str, sinh_vien_user_id: str) -> bool:
        """
        Check if a SinhVien is enrolled in a LopHocPhan
        
        Args:
            lop_hoc_phan_id: UUID of LopHocPhan
            sinh_vien_user_id: UUID of SinhVien's user account
            
        Returns:
            True if enrolled, False otherwise
        """
        pass
