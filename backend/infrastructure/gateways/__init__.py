"""
Payment Gateway Interfaces and Factory
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import os


@dataclass
class CreatePaymentRequest:
    amount: float
    order_info: str
    redirect_url: str
    ipn_url: str
    ip_addr: str = "127.0.0.1"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CreatePaymentResponse:
    pay_url: str
    order_id: str
    request_id: str


@dataclass
class VerifyIPNRequest:
    data: Dict[str, Any]


@dataclass
class VerifyIPNResponse:
    is_valid: bool
    order_id: str
    transaction_id: str
    result_code: str
    message: str


class IPaymentGateway(ABC):
    """Interface for payment gateways"""
    
    @abstractmethod
    def create_payment(self, request: CreatePaymentRequest) -> CreatePaymentResponse:
        pass
    
    @abstractmethod
    def verify_ipn(self, request: VerifyIPNRequest) -> VerifyIPNResponse:
        pass


class PaymentGatewayFactory:
    """Factory to create payment gateways"""
    
    @staticmethod
    def create(provider: str) -> IPaymentGateway:
        if provider == "momo":
            from .momo_gateway import MoMoGateway
            return MoMoGateway()
        elif provider == "vnpay":
            from .vnpay_gateway import VNPayGateway
            return VNPayGateway()
        elif provider == "zalopay":
            from .zalopay_gateway import ZaloPayGateway
            return ZaloPayGateway()
        else:
            raise ValueError(f"Unknown payment provider: {provider}")
