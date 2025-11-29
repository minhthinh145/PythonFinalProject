"""
Application Layer - Course Registration Repository Interfaces
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Any

class ILopHocPhanRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Any]:
        pass
        
    @abstractmethod
    def update_so_luong(self, id: str, amount: int) -> None:
        pass

class IDangKyHocPhanRepository(ABC):
    @abstractmethod
    def has_registered_mon_hoc_in_hoc_ky(self, sinh_vien_id: str, mon_hoc_id: str, hoc_ky_id: str) -> bool:
        pass
        
    @abstractmethod
    def is_student_registered(self, sinh_vien_id: str, lop_hoc_phan_id: str) -> bool:
        pass
        
    @abstractmethod
    def create(self, data: dict) -> Any:
        pass
        
    @abstractmethod
    def find_by_sinh_vien_and_lop_hoc_phan(self, sinh_vien_id: str, lop_hoc_phan_id: str) -> Optional[Any]:
        pass
        
    @abstractmethod
    def update_status(self, id: str, status: str) -> None:
        pass
        
    @abstractmethod
    def update_lop_hoc_phan(self, id: str, new_lop_hoc_phan_id: str) -> None:
        pass

class IDangKyTKBRepository(ABC):
    @abstractmethod
    def create(self, data: dict) -> Any:
        pass
        
    @abstractmethod
    def delete_by_dang_ky_id(self, dang_ky_id: str) -> None:
        pass
        
    @abstractmethod
    def update_lop_hoc_phan(self, dang_ky_id: str, new_lop_hoc_phan_id: str) -> None:
        pass
        
    @abstractmethod
    def find_registered_lop_hoc_phans_by_hoc_ky(self, sinh_vien_id: str, hoc_ky_id: str) -> List[Any]:
        pass

class ILichSuDangKyRepository(ABC):
    @abstractmethod
    def upsert_and_log(self, sinh_vien_id: str, hoc_ky_id: str, dang_ky_hoc_phan_id: str, hanh_dong: str) -> None:
        pass

class ILichHocDinhKyRepository(ABC):
    @abstractmethod
    def find_by_lop_hoc_phan(self, lop_hoc_phan_id: str) -> List[Any]:
        pass
