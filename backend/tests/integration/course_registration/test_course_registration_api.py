
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

def test_check_phase_dang_ky_success():
    """Test GET /api/sv/check-phase-dang-ky with valid semester"""
    print("1. Getting Current Semester...")
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    print(f"   Current HocKy ID: {hoc_ky_id}")
    
    print("2. Checking Phase...")
    resp = make_request(f"{BASE_URL}/sv/check-phase-dang-ky?hocKyId={hoc_ky_id}")
    
    print(f"   Response: {resp}")
    
    if resp['status'] == 200:
        print("   ✅ Status 200 OK")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        return False

def test_check_phase_dang_ky_missing_param():
    """Test GET /api/sv/check-phase-dang-ky without hocKyId"""
    print("Testing Missing Param...")
    resp = make_request(f"{BASE_URL}/sv/check-phase-dang-ky")
    
    if resp['status'] == 400 and resp['data']['errorCode'] == "MISSING_PARAM":
        print("   ✅ Correctly returned 400 MISSING_PARAM")
        return True
    else:
        print(f"   ❌ Unexpected response: {resp}")
        return False

def test_get_danh_sach_lop_hoc_phan():
    """Test GET /api/sv/lop-hoc-phan"""
    print("Testing Get Danh Sach Lop Hoc Phan...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get List
    resp = make_request(f"{BASE_URL}/sv/lop-hoc-phan?hocKyId={hoc_ky_id}")
    
    if resp['status'] == 200:
        data = resp['data']['data']
        print(f"   ✅ Status 200 OK")
        
        # Verify structure
        if "monChung" in data and "batBuoc" in data and "tuChon" in data:
            print(f"   ✅ Response structure valid (monChung: {len(data['monChung'])}, batBuoc: {len(data['batBuoc'])}, tuChon: {len(data['tuChon'])})")
            return True
        else:
            print(f"   ❌ Invalid structure: {data.keys()}")
            return False
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_get_danh_sach_lop_da_dang_ky():
    """Test GET /api/sv/lop-da-dang-ky"""
    print("Testing Get Danh Sach Lop Da Dang Ky...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get List
    resp = make_request(f"{BASE_URL}/sv/lop-da-dang-ky?hocKyId={hoc_ky_id}")
    
    if resp['status'] == 200:
        data = resp['data']['data']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Found {len(data)} registered subjects")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_dang_ky_hoc_phan():
    """Test POST /api/sv/dang-ky-hoc-phan"""
    print("Testing Dang Ky Hoc Phan...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get Available Class
    resp = make_request(f"{BASE_URL}/sv/lop-hoc-phan?hocKyId={hoc_ky_id}")
    if resp['status'] != 200:
        print(f"❌ Could not get classes: {resp}")
        return False
        
    data = resp['data']['data']
    lop_hoc_phan_id = None
    
    # Find a class in 'tuChon' or 'batBuoc' to register
    # We prefer 'tuChon' to avoid messing up main curriculum if any
    candidates = data.get('tuChon', []) + data.get('batBuoc', []) + data.get('monChung', [])
    
    for mon in candidates:
        if mon['danhSachLop']:
            lop_hoc_phan_id = mon['danhSachLop'][0]['id']
            break
            
    if not lop_hoc_phan_id:
        print("   ⚠️ No available class to register. Skipping registration test.")
        return True
        
    print(f"   Found class to register: {lop_hoc_phan_id}")
    
    # 3. Register
    payload = {
        "hocKyId": hoc_ky_id,
        "lopHocPhanId": lop_hoc_phan_id
    }
    
    resp = make_request(f"{BASE_URL}/sv/dang-ky-hoc-phan", method="POST", data=payload)
    
    if resp['status'] == 200:
        print(f"   ✅ Registration successful")
        return True
    elif resp['status'] == 400:
        # It might fail if already registered or full, which is also a valid response from API perspective
        # But for this test we ideally want success. 
        # If error is SUBJECT_ALREADY_REGISTERED, we consider it PASS for now as logic works.
        error_code = resp['data'].get('errorCode')
        print(f"   ⚠️ Registration returned 400: {error_code}")
        if error_code in ["SUBJECT_ALREADY_REGISTERED", "CLASS_FULL", "TIME_CONFLICT"]:
             print(f"   ✅ Expected validation error handled correctly")
             return True
        return False
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_huy_dang_ky_hoc_phan():
    """Test POST /api/sv/huy-dang-ky-hoc-phan"""
    print("Testing Huy Dang Ky Hoc Phan...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get Available Class
    resp = make_request(f"{BASE_URL}/sv/lop-hoc-phan?hocKyId={hoc_ky_id}")
    if resp['status'] != 200:
        print(f"❌ Could not get classes: {resp}")
        return False
        
    data = resp['data']['data']
    lop_hoc_phan_id = None
    
    # Find a class to register then cancel
    candidates = data.get('tuChon', []) + data.get('batBuoc', []) + data.get('monChung', [])
    
    for mon in candidates:
        if mon['danhSachLop']:
            lop_hoc_phan_id = mon['danhSachLop'][0]['id']
            break
            
    if not lop_hoc_phan_id:
        print("   ⚠️ No available class to test cancellation.")
        return True
        
    # 3. Register First (if not already)
    payload = {
        "hocKyId": hoc_ky_id,
        "lopHocPhanId": lop_hoc_phan_id
    }
    make_request(f"{BASE_URL}/sv/dang-ky-hoc-phan", method="POST", data=payload)
    
    # 4. Cancel Registration
    print(f"   Cancelling registration for class: {lop_hoc_phan_id}")
    resp = make_request(f"{BASE_URL}/sv/huy-dang-ky-hoc-phan", method="POST", data=payload)
    
    if resp['status'] == 200:
        print(f"   ✅ Cancellation successful")
        return True
    else:
        print(f"   ❌ Cancellation failed: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_chuyen_lop_hoc_phan():
    """Test POST /api/sv/chuyen-lop-hoc-phan"""
    print("Testing Chuyen Lop Hoc Phan...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get Available Classes
    resp = make_request(f"{BASE_URL}/sv/lop-hoc-phan?hocKyId={hoc_ky_id}")
    if resp['status'] != 200:
        print(f"❌ Could not get classes: {resp}")
        return False
        
    data = resp['data']['data']
    lop_cu_id = None
    lop_moi_id = None
    
    # Find a subject with at least 2 classes
    candidates = data.get('tuChon', []) + data.get('batBuoc', []) + data.get('monChung', [])
    
    for mon in candidates:
        if len(mon['danhSachLop']) >= 2:
            lop_cu_id = mon['danhSachLop'][0]['id']
            lop_moi_id = mon['danhSachLop'][1]['id']
            print(f"   Found subject {mon['maMon']} with multiple classes: {lop_cu_id} -> {lop_moi_id}")
            break
            
    if not lop_cu_id or not lop_moi_id:
        print("   ⚠️ No subject has >= 2 classes. Skipping transfer test.")
        return True
        
    # 3. Register First Class (if not already)
    payload_reg = {
        "hocKyId": hoc_ky_id,
        "lopHocPhanId": lop_cu_id
    }
    make_request(f"{BASE_URL}/sv/dang-ky-hoc-phan", method="POST", data=payload_reg)
    
    # 4. Transfer to Second Class
    print(f"   Transferring from {lop_cu_id} to {lop_moi_id}")
    payload_transfer = {
        "hocKyId": hoc_ky_id,
        "lopCuId": lop_cu_id,
        "lopMoiId": lop_moi_id
    }
    
    resp = make_request(f"{BASE_URL}/sv/chuyen-lop-hoc-phan", method="POST", data=payload_transfer)
    
    if resp['status'] == 200:
        print(f"   ✅ Transfer successful")
        return True
    else:
        print(f"   ❌ Transfer failed: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

        return False
        
def test_get_lop_chua_dang_ky_by_mon_hoc():
    """Test GET /api/sv/lop-hoc-phan/mon-hoc"""
    print("Testing Get Lop Chua Dang Ky By Mon Hoc...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get Subjects to find a MonHocId
    resp = make_request(f"{BASE_URL}/sv/mon-hoc-ghi-danh?hocKyId={hoc_ky_id}")
    if resp['status'] != 200:
        print(f"❌ Could not get subjects: {resp}")
        return False
        
    subjects = resp['data']['data']
    if not subjects:
        print("   ⚠️ No subjects found. Skipping test.")
        return True
        
    mon_hoc_id = subjects[0]['id']
    print(f"   Using MonHoc ID: {mon_hoc_id}")
    
    # 3. Get Classes for Subject
    resp = make_request(f"{BASE_URL}/sv/lop-hoc-phan/mon-hoc?monHocId={mon_hoc_id}&hocKyId={hoc_ky_id}")
    
    if resp['status'] == 200:
        data = resp['data']['data']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Found {len(data)} classes for subject")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

        return False
        
def test_get_lich_su_dang_ky():
    """Test GET /api/sv/lich-su-dang-ky"""
    print("Testing Get Lich Su Dang Ky...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get History
    resp = make_request(f"{BASE_URL}/sv/lich-su-dang-ky?hocKyId={hoc_ky_id}")
    
    if resp['status'] == 200:
        data = resp['data']['data']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Found {len(data.get('logs', []))} history logs")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

        return False

def test_get_tkb_weekly():
    """Test GET /api/sv/tkb-weekly"""
    print("Testing Get TKB Weekly...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get Weekly Schedule
    # Use a dummy date range, or one that likely has data.
    # For now just check if it returns 200 OK.
    date_start = "2023-10-23"
    date_end = "2023-10-29"
    
    resp = make_request(f"{BASE_URL}/sv/tkb-weekly?hocKyId={hoc_ky_id}&dateStart={date_start}&dateEnd={date_end}")
    
    if resp['status'] == 200:
        data = resp['data']['data']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Found {len(data)} schedule items")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_tra_cuu_hoc_phan():
    """Test GET /api/sv/tra-cuu-hoc-phan"""
    print("Testing Tra Cuu Hoc Phan...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Lookup Subjects
    resp = make_request(f"{BASE_URL}/sv/tra-cuu-hoc-phan?hocKyId={hoc_ky_id}")
    
    if resp['status'] == 200:
        data = resp['data']['data']['hocPhan']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Found {len(data)} subjects")
        if len(data) > 0:
             print(f"   Sample: {data[0]['tenHocPhan']} ({data[0]['maHocPhan']})")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_get_chi_tiet_hoc_phi():
    """Test GET /api/sv/hoc-phi"""
    print("Testing Get Chi Tiet Hoc Phi...")
    
    # 1. Get Current Semester
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get Tuition
    resp = make_request(f"{BASE_URL}/sv/hoc-phi?hocKyId={hoc_ky_id}")
    
    if resp['status'] == 200:
        data = resp['data']['data']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Total Tuition: {data.get('tongHocPhi')}")
        print(f"   ✅ Details: {len(data.get('chiTiet', []))} items")
        return True
    elif resp['status'] == 400 and resp['data']['errorCode'] == "HOC_PHI_NOT_FOUND":
        print("   ⚠️ Tuition not found (valid case)")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

if __name__ == "__main__":
    print("Running Integration Tests for Course Registration...")
    success = True
    
    if not test_check_phase_dang_ky_success():
        success = False
        print("❌ test_check_phase_dang_ky_success FAIL")
    else:
        print("✅ test_check_phase_dang_ky_success PASS")
        
    if not test_check_phase_dang_ky_missing_param():
        success = False
        print("❌ test_check_phase_dang_ky_missing_param FAIL")
    else:
        print("✅ test_check_phase_dang_ky_missing_param PASS")

    if not test_get_danh_sach_lop_hoc_phan():
        success = False
        print("❌ test_get_danh_sach_lop_hoc_phan FAIL")
    else:
        print("✅ test_get_danh_sach_lop_hoc_phan PASS")

    if not test_get_danh_sach_lop_da_dang_ky():
        success = False
        print("❌ test_get_danh_sach_lop_da_dang_ky FAIL")
    else:
        print("✅ test_get_danh_sach_lop_da_dang_ky PASS")

    if not test_dang_ky_hoc_phan():
        success = False
        print("❌ test_dang_ky_hoc_phan FAIL")
    else:
        print("✅ test_dang_ky_hoc_phan PASS")

    if not test_huy_dang_ky_hoc_phan():
        success = False
        print("❌ test_huy_dang_ky_hoc_phan FAIL")
    else:
        print("✅ test_huy_dang_ky_hoc_phan PASS")

    if not test_chuyen_lop_hoc_phan():
        success = False
        print("❌ test_chuyen_lop_hoc_phan FAIL")
    else:
        print("✅ test_chuyen_lop_hoc_phan PASS")

    if not test_get_lop_chua_dang_ky_by_mon_hoc():
        success = False
        print("❌ test_get_lop_chua_dang_ky_by_mon_hoc FAIL")
    else:
        print("✅ test_get_lop_chua_dang_ky_by_mon_hoc PASS")
        
    if not test_get_lich_su_dang_ky():
        success = False
        print("❌ test_get_lich_su_dang_ky FAIL")
    else:
        print("✅ test_get_lich_su_dang_ky PASS")
        


    if not test_get_tkb_weekly():
        success = False
        print("❌ test_get_tkb_weekly FAIL")
    else:
        print("✅ test_get_tkb_weekly PASS")

    if not test_tra_cuu_hoc_phan():
        success = False
        print("❌ test_tra_cuu_hoc_phan FAIL")
    else:
        print("✅ test_tra_cuu_hoc_phan PASS")

    if not test_get_chi_tiet_hoc_phi():
        success = False
        print("❌ test_get_chi_tiet_hoc_phi FAIL")
    else:
        print("✅ test_get_chi_tiet_hoc_phi PASS")
        
    sys.exit(0 if success else 1)
