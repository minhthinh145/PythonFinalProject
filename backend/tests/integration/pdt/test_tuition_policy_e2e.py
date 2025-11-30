import os
import sys
import django
import json
import urllib.request
import urllib.error
import uuid
from datetime import datetime, date

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
django.setup()

from infrastructure.persistence.models import HocKy, Khoa, NganhHoc, ChinhSachTinChi, HocPhi

BASE_URL = "http://localhost:8000/api"

def login():
    url = f"{BASE_URL}/auth/login"
    headers = {'Content-Type': 'application/json'}
    data = {
        "tenDangNhap": "49.01.104.145", 
        "matKhau": "123456"
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('isSuccess') or data.get('success'):
                return data['data']['token']
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def get_test_data():
    hk = HocKy.objects.using('neon').first()
    khoa = Khoa.objects.using('neon').first()
    return hk, khoa

def make_request(url, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        
    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None

def test_tuition_policy():
    print("Testing Tuition Policy...")
    
    # 1. Get Data
    hk, khoa = get_test_data()
    if not hk or not khoa:
        print("❌ Failed to get test data")
        sys.exit(1)
        
    # 2. Login
    token = login()
    if not token:
        print("❌ Login failed")
        sys.exit(1)
        
    # 3. Create Policy
    print("   3. Creating Policy...")
    policy_data = {
        "hocKyId": str(hk.id),
        "khoaId": str(khoa.id),
        "phiMoiTinChi": 500000,
        "ngayHieuLuc": "2025-01-01"
    }
    resp = make_request(f"{BASE_URL}/pdt/hoc-phi/chinh-sach", method='POST', data=policy_data, token=token)
    
    if resp and resp.get('isSuccess'):
        policy_id = resp['data']['id']
        print(f"   ✅ Created Policy: {policy_id}")
    else:
        print(f"   ❌ Create Policy Failed: {resp}")
        sys.exit(1)
        
    # 4. Get Policies
    print("   4. Getting Policies...")
    resp = make_request(f"{BASE_URL}/pdt/hoc-phi/chinh-sach", token=token)
    if resp and resp.get('isSuccess'):
        policies = resp['data']
        found = any(p['id'] == policy_id for p in policies)
        if found:
            print("   ✅ Policy found in list")
        else:
            print("   ❌ Policy NOT found in list")
            sys.exit(1)
    else:
        print("   ❌ Get Policies Failed")
        sys.exit(1)
        
    # 5. Update Policy
    print("   5. Updating Policy...")
    update_data = {
        "phiMoiTinChi": 550000
    }
    resp = make_request(f"{BASE_URL}/pdt/hoc-phi/chinh-sach/{policy_id}", method='PATCH', data=update_data, token=token)
    
    if resp and resp.get('isSuccess'):
        print("   ✅ Update Success")
    else:
        print("   ❌ Update Failed")
        sys.exit(1)
        
    # 6. Calculate Bulk Tuition
    print("   6. Calculating Bulk Tuition...")
    calc_data = {
        "hocKyId": str(hk.id)
    }
    resp = make_request(f"{BASE_URL}/pdt/hoc-phi/tinh-toan-hang-loat", method='POST', data=calc_data, token=token)
    
    if resp and resp.get('isSuccess'):
        print(f"   ✅ Calculation Success: {resp['message']}")
    else:
        print(f"   ❌ Calculation Failed: {resp}")
        sys.exit(1)
        
    print("✅ TEST PASSED")

if __name__ == "__main__":
    test_tuition_policy()
