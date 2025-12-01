import os
import sys
import django
import json
import urllib.request
import urllib.error
import uuid
import pytest

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
django.setup()

from infrastructure.persistence.models import HocKy, Khoa, NganhHoc, DangKyHocPhan

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
    return hk

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

@pytest.mark.django_db(databases=['default', 'neon'])
def test_reports():
    print("Testing Reports & Stats...")
    
    # 1. Get Data
    hk = get_test_data()
    if not hk:
        print("❌ Failed to get test data")
        sys.exit(1)
        
    # 2. Login
    token = login()
    if not token:
        print("❌ Login failed")
        sys.exit(1)
        
    # 3. Overview Stats
    print("   3. Testing Overview Stats...")
    resp = make_request(f"{BASE_URL}/bao-cao/overview?hoc_ky_id={hk.id}", token=token)
    
    if resp and resp.get('isSuccess'):
        data = resp['data']
        print(f"   ✅ Overview: {data['svUnique']} SV, {data['soDangKy']} ĐK")
    else:
        print(f"   ❌ Overview Failed: {resp}")
        sys.exit(1)
        
    # 4. Khoa Stats
    print("   4. Testing Khoa Stats...")
    resp = make_request(f"{BASE_URL}/bao-cao/dk-theo-khoa?hoc_ky_id={hk.id}", token=token)
    
    if resp and resp.get('isSuccess'):
        print(f"   ✅ Khoa Stats: {len(resp['data']['data'])} records")
    else:
        print(f"   ❌ Khoa Stats Failed: {resp}")
        sys.exit(1)

    # 5. Nganh Stats
    print("   5. Testing Nganh Stats...")
    resp = make_request(f"{BASE_URL}/bao-cao/dk-theo-nganh?hoc_ky_id={hk.id}", token=token)
    
    if resp and resp.get('isSuccess'):
        print(f"   ✅ Nganh Stats: {len(resp['data']['data'])} records")
    else:
        print(f"   ❌ Nganh Stats Failed: {resp}")
        sys.exit(1)

    # 6. Giang Vien Stats
    print("   6. Testing Giang Vien Stats...")
    resp = make_request(f"{BASE_URL}/bao-cao/tai-giang-vien?hoc_ky_id={hk.id}", token=token)
    
    if resp and resp.get('isSuccess'):
        print(f"   ✅ Giang Vien Stats: {len(resp['data']['data'])} records")
    else:
        print(f"   ❌ Giang Vien Stats Failed: {resp}")
        sys.exit(1)
        
    print("✅ TEST PASSED")

if __name__ == "__main__":
    test_reports()
