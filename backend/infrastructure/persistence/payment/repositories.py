"""
Payment Repository Implementation
"""
import uuid
from datetime import datetime
from typing import Optional
from infrastructure.persistence.models import PaymentTransactions, HocPhi


class PaymentRepository:
    """
    Repository for payment transactions
    """
    
    def create_transaction(self, sinh_vien_id: str, hoc_ky_id: str, amount: float,
                          provider: str, order_id: str, pay_url: str) -> PaymentTransactions:
        transaction = PaymentTransactions.objects.using('neon').create(
            id=uuid.uuid4(),
            sinh_vien_id=sinh_vien_id,
            hoc_ky_id=hoc_ky_id,
            amount=amount,
            provider=provider,
            order_id=order_id,
            pay_url=pay_url,
            status="pending",
            currency="VND",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return transaction
    
    def get_by_order_id(self, order_id: str) -> Optional[PaymentTransactions]:
        try:
            return PaymentTransactions.objects.using('neon').get(order_id=order_id)
        except PaymentTransactions.DoesNotExist:
            return None
    
    def update_status(self, order_id: str, status: str) -> Optional[PaymentTransactions]:
        try:
            transaction = PaymentTransactions.objects.using('neon').get(order_id=order_id)
            transaction.status = status
            transaction.updated_at = datetime.now()
            transaction.save(using='neon')
            return transaction
        except PaymentTransactions.DoesNotExist:
            return None
    
    def save_ipn_log(self, transaction_id: str, payload: dict) -> None:
        """Save IPN log for debugging"""
        from infrastructure.persistence.models import PaymentIpnLogs
        PaymentIpnLogs.objects.using('neon').create(
            id=uuid.uuid4(),
            transaction_id=transaction_id,
            received_at=datetime.now(),
            payload=payload
        )


class HocPhiPaymentRepository:
    """
    Repository for updating học phí payment status
    """
    
    def update_payment_status(self, sinh_vien_id: str, hoc_ky_id: str, status: str) -> bool:
        try:
            updated = HocPhi.objects.using('neon').filter(
                sinh_vien_id=sinh_vien_id,
                hoc_ky_id=hoc_ky_id
            ).update(
                trang_thai_thanh_toan=status,
                ngay_thanh_toan=datetime.now()
            )
            return updated > 0
        except Exception as e:
            print(f"Error updating hoc phi status: {e}")
            return False
