from abc import ABC, abstractmethod
from typing import Optional, List, Any

class IHocKyRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set_current_semester(self, hoc_ky_id: str) -> None:
        pass

    @abstractmethod
    def get_current_semester(self) -> Optional[Any]:
        pass

class IKyPhaseRepository(ABC):
    @abstractmethod
    def create_bulk(self, phases: List[dict], hoc_ky_id: str) -> List[Any]:
        pass

    @abstractmethod
    def find_by_hoc_ky(self, hoc_ky_id: str) -> List[Any]:
        pass

class IDeXuatHocPhanRepository(ABC):
    @abstractmethod
    def get_pending_proposals(self) -> List[Any]:
        pass

    @abstractmethod
    def approve_proposal(self, proposal_id: str) -> bool:
        pass

    @abstractmethod
    def reject_proposal(self, proposal_id: str) -> bool:
        pass

class IPhongHocRepository(ABC):
    @abstractmethod
    def get_available_rooms(self, start_time: Any, end_time: Any) -> List[Any]:
        pass

    @abstractmethod
    def get_by_khoa(self, khoa_id: str) -> List[Any]:
        pass

    @abstractmethod
    def assign_to_khoa(self, phong_id: str, khoa_id: str) -> bool:
        pass

    @abstractmethod
    def batch_assign_to_khoa(self, phong_ids: list, khoa_id: str) -> int:
        """Batch assign multiple rooms to khoa. Returns count of updated rooms."""
        pass

    @abstractmethod
    def unassign_from_khoa(self, phong_id: str) -> bool:
        pass

    @abstractmethod
    def batch_unassign_from_khoa(self, phong_ids: list) -> int:
        """Batch unassign multiple rooms from khoa. Returns count of updated rooms."""
        pass

class IChinhSachHocPhiRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def create(self, data: dict) -> Any:
        pass

    @abstractmethod
    def update(self, id: str, data: dict) -> bool:
        pass

    @abstractmethod
    def get_by_nganh_khoa_hoc_ky(self, nganh_id: str, khoa_id: str, hoc_ky_id: str) -> Optional[Any]:
        pass

    @abstractmethod
    def calculate_tuition_bulk(self, hoc_ky_id: str) -> int:
        # Returns number of students processed
        pass
