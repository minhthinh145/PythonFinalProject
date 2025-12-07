"""
Create Payment Use Case
"""
import os
from typing import Dict, Any
from core.types import ServiceResult


class CreatePaymentUseCase:
    """
    Creates a payment transaction and returns payment URL
    Uses real payment gateways: MoMo, VNPay, ZaloPay
    """
    
    def __init__(self, payment_repo, hoc_phi_repo):
        self.payment_repo = payment_repo
        self.hoc_phi_repo = hoc_phi_repo
    
    def execute(self, sinh_vien_id: str, hoc_ky_id: str, provider: str = "momo") -> ServiceResult[Dict[str, Any]]:
        try:
            # 1. Get hoc phi to determine amount
            hoc_phi = self.hoc_phi_repo.get_hoc_phi_by_sinh_vien(sinh_vien_id, hoc_ky_id)
            
            if not hoc_phi:
                return ServiceResult.fail(
                    message="Không tìm thấy thông tin học phí. Vui lòng tính học phí trước khi thanh toán.",
                    error_code="TUITION_NOT_FOUND"
                )
            
            # 2. Check if already paid
            if hoc_phi.trang_thai_thanh_toan == "da_thanh_toan":
                return ServiceResult.fail(
                    message="Học phí đã được thanh toán rồi",
                    error_code="ALREADY_PAID"
                )
            
            amount = float(hoc_phi.tong_hoc_phi) if hoc_phi.tong_hoc_phi else 0
            
            if amount <= 0:
                return ServiceResult.fail(
                    message="Số tiền học phí không hợp lệ",
                    error_code="INVALID_AMOUNT"
                )
            
            # 3. Create payment via gateway
            from infrastructure.gateways import PaymentGatewayFactory, CreatePaymentRequest
            
            gateway = PaymentGatewayFactory.create(provider)
            
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost")
            ipn_url = os.getenv("UNIFIED_IPN_URL", "http://localhost:8000/api/payment/ipn")
            
            # ZaloPay requires public URL for redirect, use separate env var if set
            if provider == "zalopay":
                zalopay_redirect = os.getenv("ZALOPAY_REDIRECT_URL")
                if zalopay_redirect:
                    redirect_url = f"{zalopay_redirect}/payment/result"
                else:
                    redirect_url = f"{frontend_url}/payment/result"
            else:
                redirect_url = f"{frontend_url}/payment/result"
            
            gateway_response = gateway.create_payment(CreatePaymentRequest(
                amount=amount,
                order_info=f"Thanh toan hoc phi HK {hoc_ky_id}",
                redirect_url=redirect_url,
                ipn_url=ipn_url,
                metadata={
                    "sinhVienId": sinh_vien_id,
                    "hocKyId": hoc_ky_id
                }
            ))
            
            # 4. Save transaction to DB
            transaction = self.payment_repo.create_transaction(
                sinh_vien_id=sinh_vien_id,
                hoc_ky_id=hoc_ky_id,
                amount=amount,
                provider=provider,
                order_id=gateway_response.order_id,
                pay_url=gateway_response.pay_url
            )
            
            return ServiceResult.ok({
                "payUrl": gateway_response.pay_url,
                "orderId": gateway_response.order_id,
                "amount": amount
            }, "Tạo payment thành công")
            
        except Exception as e:
            print(f"[CREATE_PAYMENT] Error: {e}")
            return ServiceResult.fail(str(e), error_code="INTERNAL_ERROR")
