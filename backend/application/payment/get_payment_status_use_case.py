"""
Get Payment Status Use Case
"""
from typing import Dict, Any
from core.types import ServiceResult


class GetPaymentStatusUseCase:
    """
    Gets status of a payment transaction
    """
    
    def __init__(self, payment_repo):
        self.payment_repo = payment_repo
    
    def execute(self, order_id: str) -> ServiceResult[Dict[str, Any]]:
        try:
            transaction = self.payment_repo.get_by_order_id(order_id)
            
            if not transaction:
                return ServiceResult.fail(
                    message="Không tìm thấy giao dịch",
                    error_code="TRANSACTION_NOT_FOUND"
                )
            
            return ServiceResult.ok({
                "orderId": transaction.order_id,
                "status": transaction.status or "pending",
                "amount": float(transaction.amount) if transaction.amount else 0,
                "createdAt": transaction.created_at.isoformat() if transaction.created_at else "",
                "updatedAt": transaction.updated_at.isoformat() if transaction.updated_at else ""
            })
            
        except Exception as e:
            print(f"Error getting payment status: {e}")
            return ServiceResult.fail(str(e), error_code="INTERNAL_ERROR")
