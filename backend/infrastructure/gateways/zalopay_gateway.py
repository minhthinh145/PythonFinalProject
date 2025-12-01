"""
ZaloPay Payment Gateway Implementation
"""
import os
import hashlib
import hmac
import json
import requests
from datetime import datetime
from . import IPaymentGateway, CreatePaymentRequest, CreatePaymentResponse, VerifyIPNRequest, VerifyIPNResponse


class ZaloPayGateway(IPaymentGateway):
    """ZaloPay Payment Gateway"""
    
    def __init__(self):
        self.app_id = os.getenv("ZALOPAY_APP_ID", "")
        self.key1 = os.getenv("ZALOPAY_KEY1", "")
        self.key2 = os.getenv("ZALOPAY_KEY2", "")
        self.endpoint = os.getenv("ZALOPAY_ENDPOINT", "https://sb-openapi.zalopay.vn")
    
    def create_payment(self, request: CreatePaymentRequest) -> CreatePaymentResponse:
        app_time = int(datetime.now().timestamp() * 1000)
        trans_id = int(datetime.now().timestamp()) % 1000000
        
        # ZaloPay app_trans_id format: yyMMdd_transId
        app_trans_id = f"{datetime.now().strftime('%y%m%d')}_{trans_id}"
        
        sinh_vien_id = request.metadata.get("sinhVienId", "UNKNOWN") if request.metadata else "UNKNOWN"
        
        embed_data = json.dumps({
            "redirecturl": request.redirect_url,
            "merchant_order_id": f"ORDER_{app_time}_{sinh_vien_id[:8]}"
        })
        
        items = json.dumps([{
            "itemid": app_trans_id,
            "itemname": request.order_info,
            "itemprice": int(request.amount),
            "itemquantity": 1
        }])
        
        # Build MAC: app_id|app_trans_id|app_user|amount|app_time|embed_data|item
        data = f"{self.app_id}|{app_trans_id}|user123|{int(request.amount)}|{app_time}|{embed_data}|{items}"
        mac = hmac.new(
            self.key1.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        payload = {
            "app_id": int(self.app_id),
            "app_trans_id": app_trans_id,
            "app_user": "user123",
            "app_time": app_time,
            "amount": int(request.amount),
            "item": items,
            "embed_data": embed_data,
            "description": request.order_info,
            "bank_code": "",
            "callback_url": request.ipn_url,
            "mac": mac
        }
        
        response = requests.post(
            f"{self.endpoint}/v2/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        if result.get("return_code") != 1:
            raise Exception(f"ZaloPay error: {result.get('return_message', 'Unknown error')}")
        
        return CreatePaymentResponse(
            pay_url=result.get("order_url", ""),
            order_id=app_trans_id,
            request_id=app_trans_id
        )
    
    def verify_ipn(self, request: VerifyIPNRequest) -> VerifyIPNResponse:
        data = request.data
        
        received_mac = data.get("mac", "")
        data_str = data.get("data", "")
        
        # Verify MAC using key2
        calculated_mac = hmac.new(
            self.key2.encode('utf-8'),
            data_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = calculated_mac == received_mac
        
        # Parse data JSON
        try:
            data_json = json.loads(data_str)
        except json.JSONDecodeError:
            data_json = {}
        
        return VerifyIPNResponse(
            is_valid=is_valid,
            order_id=data_json.get("app_trans_id", ""),
            transaction_id=str(data_json.get("zp_trans_id", "")),
            result_code="1" if is_valid else "0",
            message="Success" if is_valid else "Invalid signature"
        )
