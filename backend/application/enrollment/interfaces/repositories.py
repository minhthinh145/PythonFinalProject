"""
Application Layer - Enrollment Repository Interfaces
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Any

class IHocKyRepository(ABC):
    @abstractmethod
    def get_current_hoc_ky(self) -> Optional[Any]:
        pass

    @abstractmethod
    def get_all_hoc_ky(self) -> List[Any]:
        pass

    @abstractmethod
    def update_dates(self, id: str, start_at: Any, end_at: Any) -> None:
        pass



class IKhoaRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

class IHocPhiRepository(ABC):
    @abstractmethod
    def get_hoc_phi_by_sinh_vien(self, sinh_vien_id: str, hoc_ky_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def create_bulk(self, phases: List[dict], hoc_ky_id: str) -> List[dict]:
        pass

class IKyPhaseRepository(ABC):
    @abstractmethod
    def get_current_phase(self, hoc_ky_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def create_bulk(self, phases: List[dict], hoc_ky_id: str) -> List[dict]:
        pass

    @abstractmethod
    def find_by_hoc_ky(self, hoc_ky_id: str) -> List[Any]:
        pass

class IDotDangKyRepository(ABC):
    @abstractmethod
    def find_toan_truong_by_hoc_ky(self, hoc_ky_id: str, phase: str) -> Optional[Any]:
        pass
        
    @abstractmethod
    def is_ghi_danh_for_khoa(self, khoa_id: str, hoc_ky_id: str) -> bool:
        pass

    @abstractmethod
    def find_active_dot_dang_ky(self, hoc_ky_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def create(self, data: dict) -> Any:
        pass

    @abstractmethod
    def find_by_hoc_ky_and_loai(self, hoc_ky_id: str, loai_dot: str) -> List[Any]:
        pass

    @abstractmethod
    def update(self, id: str, data: dict) -> Optional[Any]:
        pass

class IGhiDanhRepository(ABC):
    @abstractmethod
    def is_already_registered(self, sinh_vien_id: str, hoc_phan_id: str) -> bool:
        pass
        
    @abstractmethod
    def create(self, data: dict) -> Any:
        pass
        
    @abstractmethod
    def find_by_sinh_vien(self, sinh_vien_id: str) -> List[Any]:
        pass
        
    @abstractmethod
    def delete_many(self, ids: List[str]) -> None:
        pass
        
    @abstractmethod
    def find_by_ids(self, ids: List[str]) -> List[Any]:
        pass

class IHocPhanRepository(ABC):
    @abstractmethod
    def find_all_open(self, hoc_ky_id: str) -> List[Any]:
        pass
        
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Any]:
        pass
