"""
VNPay Payment Gateway Implementation
"""
import os
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from . import IPaymentGateway, CreatePaymentRequest, CreatePaymentResponse, VerifyIPNRequest, VerifyIPNResponse


class VNPayGateway(IPaymentGateway):
    """VNPay Payment Gateway"""
    
    def __init__(self):
        self.tmn_code = os.getenv("VNPAY_TMN_CODE", "")
        self.secret_key = os.getenv("VNPAY_SECRET_KEY", "")
        self.endpoint = os.getenv("VNPAY_ENDPOINT", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
    
    def create_payment(self, request: CreatePaymentRequest) -> CreatePaymentResponse:
        # Generate orderId from metadata
        sinh_vien_id = request.metadata.get("sinhVienId", "UNKNOWN") if request.metadata else "UNKNOWN"
        order_id = f"ORDER_{int(datetime.now().timestamp() * 1000)}_{sinh_vien_id[:8]}"
        
        now = datetime.now()
        expire = now + timedelta(days=1)
        
        # VNPay params (alphabetical order for signature)
        params = {
            "vnp_Amount": int(request.amount * 100),  # VNPay uses VND * 100
            "vnp_Command": "pay",
            "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
            "vnp_CurrCode": "VND",
            "vnp_ExpireDate": expire.strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": request.ip_addr,
            "vnp_Locale": "vn",
            "vnp_OrderInfo": request.order_info,
            "vnp_OrderType": "other",
            "vnp_ReturnUrl": request.redirect_url,
            "vnp_TmnCode": self.tmn_code,
            "vnp_TxnRef": order_id,
            "vnp_Version": "2.1.0",
        }
        
        # Sort params and build query string
        sorted_params = sorted(params.items())
        query_string = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params)
        
        # Create signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        pay_url = f"{self.endpoint}?{query_string}&vnp_SecureHash={signature}"
        
        return CreatePaymentResponse(
            pay_url=pay_url,
            order_id=order_id,
            request_id=order_id
        )
    
    def verify_ipn(self, request: VerifyIPNRequest) -> VerifyIPNResponse:
        data = request.data
        
        # Extract signature
        received_signature = data.pop("vnp_SecureHash", "")
        data.pop("vnp_SecureHashType", None)
        
        # Sort and rebuild query string
        sorted_params = sorted(data.items())
        query_string = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params)
        
        # Calculate signature
        calculated_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        is_valid = calculated_signature.lower() == received_signature.lower()
        is_success = data.get("vnp_ResponseCode") == "00"
        
        return VerifyIPNResponse(
            is_valid=is_valid and is_success,
            order_id=data.get("vnp_TxnRef", ""),
            transaction_id=str(data.get("vnp_TransactionNo", "")),
            result_code=str(data.get("vnp_ResponseCode", "")),
            message="Success" if is_valid and is_success else "Failed"
        )
