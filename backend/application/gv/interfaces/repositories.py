"""
Application Layer - GV Repository Interfaces

Contracts for infrastructure layer implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import date


# ============== DTOs ==============

@dataclass
class GVLopHocPhanDTO:
    """DTO for GV's class list - map 1-1 với frontend GVLopHocPhanDTO"""
    id: str
    ma_lop: str
    so_luong_hien_tai: Optional[int]
    so_luong_toi_da: Optional[int]
    hoc_phan: Dict[str, Any]  # Contains ten_hoc_phan, mon_hoc


@dataclass
class GVLopHocPhanDetailDTO:
    """DTO for GV's class detail - map 1-1 với frontend GVLopHocPhanDetailDTO"""
    id: str
    ma_lop: str
    hoc_phan: Dict[str, Any]  # Contains ten_hoc_phan, mon_hoc


@dataclass
class GVStudentDTO:
    """DTO for student in class - map 1-1 với frontend GVStudentDTO"""
    id: str  # UUID sinh viên
    mssv: str
    hoTen: str
    lop: Optional[str]
    email: str


@dataclass
class GVGradeDTO:
    """DTO for student grade - map 1-1 với frontend GVGradeDTO"""
    sinh_vien_id: str  # UUID sinh viên
    diem_so: Optional[float]


@dataclass
class GVTKBItemDTO:
    """DTO for TKB item - map 1-1 với frontend TKBWeeklyItemDTO"""
    lop_hoc_phan_id: str
    ma_lop: str
    ten_mon: str
    ma_mon: str
    phong: Optional[str]
    thu: int
    tiet_bat_dau: int
    tiet_ket_thuc: int
    ngay_hoc: str  # YYYY-MM-DD format


# ============== Interfaces ==============

class IGVLopHocPhanRepository(ABC):
    """Repository interface for GV's Lop Hoc Phan operations"""

    @abstractmethod
    def get_lop_hoc_phan_by_gv(
        self, 
        gv_user_id: str, 
        hoc_ky_id: Optional[str] = None
    ) -> List[GVLopHocPhanDTO]:
        """
        Get all LopHocPhan assigned to a GiangVien
        
        Args:
            gv_user_id: UUID of the GiangVien's user account
            hoc_ky_id: Optional filter by semester
            
        Returns:
            List of GVLopHocPhanDTO
        """
        pass

    @abstractmethod
    def get_lop_hoc_phan_detail(
        self, 
        lhp_id: str, 
        gv_user_id: str
    ) -> Optional[GVLopHocPhanDetailDTO]:
        """
        Get detail of a LopHocPhan (only if GV is assigned)
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of the GiangVien's user account
            
        Returns:
            GVLopHocPhanDetailDTO or None if not found/not authorized
        """
        pass

    @abstractmethod
    def get_students_of_lhp(
        self, 
        lhp_id: str, 
        gv_user_id: str
    ) -> Optional[List[GVStudentDTO]]:
        """
        Get registered students of a LopHocPhan (only if GV is assigned)
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of the GiangVien's user account
            
        Returns:
            List of GVStudentDTO or None if not authorized
        """
        pass

    @abstractmethod
    def verify_gv_owns_lhp(self, lhp_id: str, gv_user_id: str) -> bool:
        """
        Check if GV is assigned to the LopHocPhan
        
        Args:
            lhp_id: UUID of LopHocPhan
            gv_user_id: UUID of the GiangVien's user account
            
        Returns:
            True if GV owns this LHP
        """
        pass


class IGVGradeRepository(ABC):
    """Repository interface for GV's grade operations"""

    @abstractmethod
    def get_grades(
        self, 
        lhp_id: str
    ) -> List[GVGradeDTO]:
        """
        Get all grades for a LopHocPhan
        
        Args:
            lhp_id: UUID of LopHocPhan
            
        Returns:
            List of GVGradeDTO
        """
        pass

    @abstractmethod
    def upsert_grades(
        self, 
        lhp_id: str, 
        grades: List[Dict[str, Any]]
    ) -> bool:
        """
        Insert or update grades for students
        
        Args:
            lhp_id: UUID of LopHocPhan
            grades: List of {sinh_vien_id, diem_so}
            
        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def validate_students_in_lhp(
        self, 
        lhp_id: str, 
        sinh_vien_ids: List[str]
    ) -> bool:
        """
        Validate that all sinh_vien_ids are registered in the LHP
        
        Args:
            lhp_id: UUID of LopHocPhan
            sinh_vien_ids: List of student UUIDs
            
        Returns:
            True if all students are registered
        """
        pass


class IGVTKBRepository(ABC):
    """Repository interface for GV's TKB (Timetable) operations"""

    @abstractmethod
    def get_tkb_weekly(
        self, 
        gv_user_id: str,
        hoc_ky_id: str,
        date_start: date,
        date_end: date
    ) -> List[GVTKBItemDTO]:
        """
        Get weekly timetable for a GiangVien
        
        Args:
            gv_user_id: UUID of the GiangVien's user account
            hoc_ky_id: UUID of HocKy
            date_start: Start date of week
            date_end: End date of week
            
        Returns:
            List of GVTKBItemDTO
        """
        pass
