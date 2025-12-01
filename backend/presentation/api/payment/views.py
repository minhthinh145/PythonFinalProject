"""
Payment API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from application.payment.create_payment_use_case import CreatePaymentUseCase
from application.payment.get_payment_status_use_case import GetPaymentStatusUseCase
from application.payment.process_ipn_use_case import ProcessIPNUseCase
from infrastructure.persistence.payment.repositories import PaymentRepository, HocPhiPaymentRepository
from infrastructure.persistence.course_registration.repositories import HocPhiRepository


class CreatePaymentView(APIView):
    """
    POST /api/payment/create
    
    Create a payment transaction
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        hoc_ky_id = request.data.get('hocKyId')
        provider = request.data.get('provider', 'momo')
        
        if not hoc_ky_id:
            return Response({
                "success": False,
                "message": "Thiếu thông tin học kỳ (hocKyId)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
        
        # Validate provider
        if provider not in ['momo', 'vnpay', 'zalopay']:
            return Response({
                "success": False,
                "message": "Provider không hợp lệ. Chọn: momo, vnpay, zalopay",
                "errorCode": "INVALID_PROVIDER"
            }, status=400)
        
        use_case = CreatePaymentUseCase(
            PaymentRepository(),
            HocPhiRepository()
        )
        
        result = use_case.execute(str(request.user.id), hoc_ky_id, provider)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class GetPaymentStatusView(APIView):
    """
    GET /api/payment/status
    
    Get payment transaction status
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        order_id = request.query_params.get('orderId') or request.query_params.get('order_id')
        
        if not order_id:
            return Response({
                "success": False,
                "message": "Thiếu mã giao dịch (orderId)",
                "errorCode": "MISSING_PARAM"
            }, status=400)
        
        use_case = GetPaymentStatusUseCase(PaymentRepository())
        
        result = use_case.execute(order_id)
        
        return Response(result.to_dict(), status=result.status_code or 200)


class PaymentIPNView(APIView):
    """
    POST /api/payment/ipn
    
    Unified IPN handler for all payment providers
    """
    permission_classes = [AllowAny]  # IPN callbacks don't have auth
    
    def post(self, request):
        data = request.data
        
        # Detect provider from data
        provider = self._detect_provider(data)
        
        if not provider:
            return Response({
                "success": False,
                "message": "Cannot detect payment provider"
            }, status=400)
        
        print(f"[IPN] Received from {provider}: {data}")
        
        use_case = ProcessIPNUseCase(
            PaymentRepository(),
            HocPhiPaymentRepository()
        )
        
        result = use_case.execute(provider, dict(data))
        
        # Return appropriate response based on provider
        if provider == "momo":
            return Response({"resultCode": 0, "message": "OK"})
        elif provider == "vnpay":
            return Response({"RspCode": "00", "Message": "Confirm Success"})
        elif provider == "zalopay":
            return Response({"return_code": 1, "return_message": "Success"})
        
        return Response(result.to_dict())
    
    def _detect_provider(self, data: dict) -> str:
        """Detect payment provider from IPN data"""
        if "partnerCode" in data or "orderId" in data and "transId" in data:
            return "momo"
        elif "vnp_TxnRef" in data or "vnp_ResponseCode" in data:
            return "vnpay"
        elif "data" in data and "mac" in data:
            return "zalopay"
        return ""
