"""
Process IPN (Instant Payment Notification) Use Case
Handles callbacks from payment gateways
"""
from typing import Dict, Any
from core.types import ServiceResult


class ProcessIPNUseCase:
    """
    Processes IPN callbacks from payment gateways
    Updates payment status and học phí status
    """
    
    def __init__(self, payment_repo, hoc_phi_repo):
        self.payment_repo = payment_repo
        self.hoc_phi_repo = hoc_phi_repo
    
    def execute(self, provider: str, data: Dict[str, Any]) -> ServiceResult[Dict[str, Any]]:
        try:
            from infrastructure.gateways import PaymentGatewayFactory, VerifyIPNRequest
            
            # 1. Get gateway and verify IPN
            gateway = PaymentGatewayFactory.create(provider)
            verify_result = gateway.verify_ipn(VerifyIPNRequest(data=data))
            
            if not verify_result.is_valid:
                print(f"[IPN] Invalid signature for order {verify_result.order_id}")
                return ServiceResult.fail(
                    message="Invalid IPN signature",
                    error_code="INVALID_SIGNATURE"
                )
            
            # 2. Get transaction
            transaction = self.payment_repo.get_by_order_id(verify_result.order_id)
            
            if not transaction:
                print(f"[IPN] Transaction not found: {verify_result.order_id}")
                return ServiceResult.fail(
                    message="Transaction not found",
                    error_code="TRANSACTION_NOT_FOUND"
                )
            
            # 3. Check if payment successful
            is_success = self._is_payment_successful(provider, verify_result.result_code)
            
            if is_success:
                # Update transaction status
                self.payment_repo.update_status(verify_result.order_id, "success")
                
                # Update học phí status
                self.hoc_phi_repo.update_payment_status(
                    str(transaction.sinh_vien_id),
                    str(transaction.hoc_ky_id),
                    "da_thanh_toan"
                )
                
                print(f"[IPN] Payment successful: {verify_result.order_id}")
            else:
                self.payment_repo.update_status(verify_result.order_id, "failed")
                print(f"[IPN] Payment failed: {verify_result.order_id}, code: {verify_result.result_code}")
            
            return ServiceResult.ok({
                "orderId": verify_result.order_id,
                "status": "success" if is_success else "failed",
                "transactionId": verify_result.transaction_id
            })
            
        except Exception as e:
            print(f"[IPN] Error processing: {e}")
            return ServiceResult.fail(str(e), error_code="INTERNAL_ERROR")
    
    def _is_payment_successful(self, provider: str, result_code: str) -> bool:
        """Check if payment was successful based on provider's result code"""
        if provider == "momo":
            return result_code == "0"
        elif provider == "vnpay":
            return result_code == "00"
        elif provider == "zalopay":
            return result_code == "1"
        return False
