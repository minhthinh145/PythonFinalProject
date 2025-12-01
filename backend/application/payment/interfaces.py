"""
Payment use cases
"""
from abc import ABC, abstractmethod
from typing import Optional
from infrastructure.persistence.models import PaymentTransactions, HocPhi


class IPaymentRepository(ABC):
    @abstractmethod
    def create_transaction(self, sinh_vien_id: str, hoc_ky_id: str, amount: float, 
                          provider: str, order_id: str, pay_url: str) -> PaymentTransactions:
        pass
    
    @abstractmethod
    def get_by_order_id(self, order_id: str) -> Optional[PaymentTransactions]:
        pass
    
    @abstractmethod
    def update_status(self, order_id: str, status: str) -> Optional[PaymentTransactions]:
        pass


class IHocPhiRepository(ABC):
    @abstractmethod
    def get_hoc_phi_by_sinh_vien(self, sinh_vien_id: str, hoc_ky_id: str) -> Optional[HocPhi]:
        pass
    
    @abstractmethod
    def update_payment_status(self, sinh_vien_id: str, hoc_ky_id: str, status: str) -> bool:
        pass
