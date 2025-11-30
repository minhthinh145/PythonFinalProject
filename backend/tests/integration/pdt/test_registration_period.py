import urllib.request
import json
import urllib.error
import sys

BASE_URL = "http://localhost:8000/api"
# Token from previous session (valid for 24h)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0NDgzMzI1LCJpYXQiOjE3NjQzOTY5MjUsImp0aSI6IjM1MDFjNWE4OTQ1YjRmMGNiY2U1MGYzNWY4MTM0ODQ0IiwidXNlcl9pZCI6ImE0ZjhhNzAyLTU0ZDgtNGZiNy1iNTgxLWU2OWE1OTkxZTk5NCIsInJvbGUiOiJzaW5oX3ZpZW4ifQ.i0SYhFKZ9-pnuexnKZbAc8TRs99ek-PCbzlKzuGHi2I"

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    
    if data:
        req.data = json.dumps(data).encode('utf-8')
        
    try:
        with urllib.request.urlopen(req) as response:
            raw_data = response.read().decode('utf-8')
            try:
                return {
                    "status": response.status,
                    "data": json.loads(raw_data)
                }
            except json.JSONDecodeError:
                print(f"❌ JSON Decode Error. Raw response: {raw_data}")
                return {
                    "status": response.status,
                    "data": raw_data
                }
    except urllib.error.HTTPError as e:
        raw_data = e.read().decode('utf-8')
        try:
            data = json.loads(raw_data)
        except:
            data = raw_data
            print(f"❌ JSON Decode Error (HTTP {e.code}). Raw response: {raw_data}")
            
        return {
            "status": e.code,
            "data": data
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def login():
    print("   Logging in...")
    payload = {
        "tenDangNhap": "49.01.104.145",
        "matKhau": "123456"
    }
    
    req = urllib.request.Request(f"{BASE_URL}/auth/login", method="POST")
    req.add_header('Content-Type', 'application/json')
    req.data = json.dumps(payload).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            # Check for isSuccess (standard) or success (legacy)
            if data.get('isSuccess') or data.get('success'):
                token = data['data']['token']
                print("   ✅ Login successful")
                return token
            else:
                print(f"   ❌ Login failed: {data.get('message', 'Unknown error')}")
                return None
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def test_registration_period_management():
    """
    Test flow:
    1. Login
    2. Get Current Semester
    3. Get Khoa List
    4. Update DotGhiDanh
    5. Get DotGhiDanh
    6. Update DotDangKy
    7. Get DotDangKy
    """
    print("Testing Registration Period Management...")
    
    # 1. Login
    global TOKEN
    TOKEN = login()
    if not TOKEN:
        return False
    
    # 2. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    print(f"   Using HocKy ID: {hoc_ky_id}")
    
    # 3. Get Khoa List
    print("   3. Getting Khoa List...")
    resp = make_request(f"{BASE_URL}/pdt/khoa")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get khoa list: {resp}")
        return False

    khoa_list = resp['data']['data']
    if not khoa_list:
        print("❌ No Khoa found")
        return False
        
    khoa_id = khoa_list[0]['id']
    print(f"   Using Khoa ID: {khoa_id}")

    # 4. Update DotGhiDanh
    print("   4. Updating DotGhiDanh...")
    payload = {
        'hocKyId': hoc_ky_id,
        'khoaId': khoa_id,
        'thoiGianBatDau': '2024-01-01T00:00:00Z',
        'thoiGianKetThuc': '2024-01-15T23:59:59Z'
    }
    resp = make_request(f"{BASE_URL}/pdt/dot-ghi-danh/update", method="POST", data=payload)
    
    if resp['status'] == 200 and resp['data']['isSuccess']:
        print("   ✅ Update DotGhiDanh Success")
    else:
        print(f"   ❌ Update DotGhiDanh Failed: {resp}")
        return False
        
    # 5. Get DotGhiDanh
    print("   5. Getting DotGhiDanh...")
    resp = make_request(f"{BASE_URL}/pdt/dot-dang-ky/{hoc_ky_id}")
    
    if resp['status'] == 200 and resp['data']['isSuccess']:
        data = resp['data']['data']
        # Note: data is a list of DotDangKy. We need to check if our updated one is there.
        # Since we just updated/created it, it should be there.
        # But wait, GetDotGhiDanhByHocKyUseCase returns what?
        # It returns DotDangKy with loai_dot='ghi_danh'.
        if len(data) >= 1:
             # Check if any item matches our khoaId
             found = False
             for item in data:
                 if item.get('khoaId') == khoa_id:
                     found = True
                     break
             if found:
                 print("   ✅ Get DotGhiDanh Success")
             else:
                 print(f"   ❌ Get DotGhiDanh Failed (Khoa ID mismatch): {data}")
                 return False
        else:
             print(f"   ❌ Get DotGhiDanh Failed (Empty list): {data}")
             return False
    else:
        print(f"   ❌ Get DotGhiDanh Failed: {resp}")
        return False
        
    # 6. Update DotDangKy
    print("   6. Updating DotDangKy...")
    payload = {
        'hocKyId': hoc_ky_id,
        'loaiDot': 'dang_ky',
        'thoiGianBatDau': '2024-01-16T00:00:00Z',
        'thoiGianKetThuc': '2024-01-30T23:59:59Z',
        'isCheckToanTruong': True
    }
    resp = make_request(f"{BASE_URL}/pdt/dot-dang-ky", method="PUT", data=payload)
    
    if resp['status'] == 200 and resp['data']['isSuccess']:
        print("   ✅ Update DotDangKy Success")
    else:
        print(f"   ❌ Update DotDangKy Failed: {resp}")
        return False
        
    # 7. Get DotDangKy
    print("   7. Getting DotDangKy...")
    resp = make_request(f"{BASE_URL}/pdt/dot-dang-ky?hoc_ky_id={hoc_ky_id}")
    
    if resp['status'] == 200 and resp['data']['isSuccess']:
        data = resp['data']['data']
        found = False
        for dot in data:
            if dot['loaiDot'] == 'dang_ky':
                found = True
                if dot['isCheckToanTruong'] is True:
                    print("   ✅ Get DotDangKy Success")
                else:
                    print("   ❌ Get DotDangKy Failed (isCheckToanTruong mismatch)")
                    return False
                break
        if not found:
            print("   ❌ Get DotDangKy Failed (Not found)")
            return False
    else:
        print(f"   ❌ Get DotDangKy Failed: {resp}")
        return False
        
    return True

if __name__ == "__main__":
    print("Running E2E Tests for Registration Period...")
    if test_registration_period_management():
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED")
        sys.exit(1)
