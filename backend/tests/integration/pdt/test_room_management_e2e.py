import os
import sys
import django
import json
import urllib.request
import urllib.error
import uuid
from datetime import datetime

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
django.setup()

from infrastructure.persistence.models import Phong, Khoa, CoSo

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

def create_test_data():
    try:
        # Ensure CoSo exists
        coso = CoSo.objects.using('neon').first()
        if not coso:
            coso = CoSo.objects.using('neon').create(
                id=uuid.uuid4(),
                ten_co_so="Co So Test",
                dia_chi="Test Address"
            )
            
        # Create a test room (unassigned)
        room = Phong.objects.using('neon').create(
            id=uuid.uuid4(),
            ma_phong=f"P{uuid.uuid4().hex[:4]}",
            co_so=coso,
            suc_chua=50,
            da_dc_su_dung=False,
            khoa=None
        )
        
        # Ensure Khoa exists
        khoa = Khoa.objects.using('neon').first()
        
        return room, khoa
    except Exception as e:
        print(f"Error creating test data: {e}")
        return None, None

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

def test_room_management():
    print("Testing Room Management...")
    
    # 1. Create Data
    room, khoa = create_test_data()
    if not room or not khoa:
        print("❌ Failed to create test data")
        sys.exit(1)
    print(f"   Created Room: {room.ma_phong}, Khoa: {khoa.ten_khoa}")

    # 2. Login
    token = login()
    if not token:
        print("❌ Login failed")
        sys.exit(1)
        
    # 3. Get Available Rooms
    print("   3. Getting Available Rooms...")
    resp = make_request(f"{BASE_URL}/pdt/phong-hoc/available", token=token)
    if resp and resp.get('isSuccess'):
        rooms = resp['data']
        found_room = next((r for r in rooms if r['id'] == str(room.id)), None)
        if found_room:
            print("   ✅ Room found in available list")
            # Verify camelCase
            if 'maPhong' in found_room and 'sucChua' in found_room and 'tenCoSo' in found_room:
                 print("   ✅ Response has camelCase fields (maPhong, sucChua, tenCoSo)")
            else:
                 print(f"   ❌ Response missing camelCase fields: {found_room.keys()}")
                 sys.exit(1)
        else:
            print("   ❌ Room NOT found in available list")
            sys.exit(1)
    else:
        print("   ❌ Failed to get available rooms")
        sys.exit(1)
        
    # 4. Assign Room
    print("   4. Assigning Room to Khoa...")
    resp = make_request(f"{BASE_URL}/pdt/phong-hoc/assign", method='POST', data={
        'phongId': str(room.id),
        'khoaId': str(khoa.id)
    }, token=token)
    
    if resp and resp.get('isSuccess'):
        print("   ✅ Assign Success")
    else:
        print("   ❌ Assign Failed")
        sys.exit(1)
        
    # 5. Verify in Khoa List
    print("   5. Verifying in Khoa List...")
    resp = make_request(f"{BASE_URL}/pdt/phong-hoc/khoa/{khoa.id}", token=token)
    if resp and resp.get('isSuccess'):
        rooms = resp['data']
        found = any(r['id'] == str(room.id) for r in rooms)
        if found:
            print("   ✅ Room found in Khoa list")
        else:
            print("   ❌ Room NOT found in Khoa list")
            sys.exit(1)
    else:
        print("   ❌ Failed to get Khoa rooms")
        sys.exit(1)
        
    # 6. Unassign Room
    print("   6. Unassigning Room...")
    resp = make_request(f"{BASE_URL}/pdt/phong-hoc/unassign", method='POST', data={
        'phongId': str(room.id)
    }, token=token)
    
    if resp and resp.get('isSuccess'):
        print("   ✅ Unassign Success")
    else:
        print("   ❌ Unassign Failed")
        sys.exit(1)
        
    # 7. Verify back in Available
    print("   7. Verifying back in Available...")
    resp = make_request(f"{BASE_URL}/pdt/phong-hoc/available", token=token)
    if resp and resp.get('isSuccess'):
        rooms = resp['data']
        found = any(r['id'] == str(room.id) for r in rooms)
        if found:
            print("   ✅ Room found in available list")
        else:
            print("   ❌ Room NOT found in available list")
            sys.exit(1)
    else:
        print("   ❌ Failed to get available rooms")
        sys.exit(1)
        
    print("✅ TEST PASSED")

if __name__ == "__main__":
    test_room_management()
