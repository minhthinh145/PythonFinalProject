"""
MoMo Payment Gateway Implementation
"""
import os
import hashlib
import hmac
import requests
from datetime import datetime
from . import IPaymentGateway, CreatePaymentRequest, CreatePaymentResponse, VerifyIPNRequest, VerifyIPNResponse


class MoMoGateway(IPaymentGateway):
    """MoMo Payment Gateway"""
    
    def __init__(self):
        self.access_key = os.getenv("MOMO_ACCESS_KEY", "")
        self.secret_key = os.getenv("MOMO_SECRET_KEY", "")
        self.partner_code = os.getenv("MOMO_PARTNER_CODE", "MOMO")
        self.endpoint = os.getenv("MOMO_ENDPOINT", "https://test-payment.momo.vn")
    
    def create_payment(self, request: CreatePaymentRequest) -> CreatePaymentResponse:
        # Generate orderId from metadata
        sinh_vien_id = request.metadata.get("sinhVienId", "UNKNOWN") if request.metadata else "UNKNOWN"
        order_id = f"ORDER_{int(datetime.now().timestamp() * 1000)}_{sinh_vien_id[:8]}"
        
        extra_data = ""
        request_type = "payWithMethod"
        
        # Build signature
        raw_signature = (
            f"accessKey={self.access_key}"
            f"&amount={int(request.amount)}"
            f"&extraData={extra_data}"
            f"&ipnUrl={request.ipn_url}"
            f"&orderId={order_id}"
            f"&orderInfo={request.order_info}"
            f"&partnerCode={self.partner_code}"
            f"&redirectUrl={request.redirect_url}"
            f"&requestId={order_id}"
            f"&requestType={request_type}"
        )
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Send request to MoMo
        payload = {
            "partnerCode": self.partner_code,
            "accessKey": self.access_key,
            "requestId": order_id,
            "amount": int(request.amount),
            "orderId": order_id,
            "orderInfo": request.order_info,
            "redirectUrl": request.redirect_url,
            "ipnUrl": request.ipn_url,
            "requestType": request_type,
            "extraData": extra_data,
            "signature": signature,
            "lang": "vi"
        }
        
        response = requests.post(
            f"{self.endpoint}/v2/gateway/api/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        data = response.json()
        
        if data.get("resultCode") != 0:
            raise Exception(f"MoMo error: {data.get('message', 'Unknown error')}")
        
        return CreatePaymentResponse(
            pay_url=data.get("payUrl", ""),
            order_id=order_id,
            request_id=data.get("requestId", order_id)
        )
    
    def verify_ipn(self, request: VerifyIPNRequest) -> VerifyIPNResponse:
        data = request.data
        
        # Extract fields for signature verification
        received_signature = data.get("signature", "")
        
        raw_signature = (
            f"accessKey={self.access_key}"
            f"&amount={data.get('amount', 0)}"
            f"&extraData={data.get('extraData', '')}"
            f"&message={data.get('message', '')}"
            f"&orderId={data.get('orderId', '')}"
            f"&orderInfo={data.get('orderInfo', '')}"
            f"&orderType={data.get('orderType', '')}"
            f"&partnerCode={self.partner_code}"
            f"&payType={data.get('payType', '')}"
            f"&requestId={data.get('requestId', '')}"
            f"&responseTime={data.get('responseTime', '')}"
            f"&resultCode={data.get('resultCode', '')}"
            f"&transId={data.get('transId', '')}"
        )
        
        calculated_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = calculated_signature == received_signature
        
        return VerifyIPNResponse(
            is_valid=is_valid,
            order_id=data.get("orderId", ""),
            transaction_id=str(data.get("transId", "")),
            result_code=str(data.get("resultCode", "")),
            message=data.get("message", "")
        )
