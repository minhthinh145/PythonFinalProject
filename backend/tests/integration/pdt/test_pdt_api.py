
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

def test_set_hoc_ky_hien_hanh():
    """Test POST /api/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh"""
    print("Testing Set Hoc Ky Hien Hanh...")
    
    # 1. Get a Semester ID (using public API)
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    print(f"   Using HocKy ID: {hoc_ky_id}")
    

    payload = {"hocKyId": hoc_ky_id}
    resp = make_request(f"{BASE_URL}/pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh", method="POST", data=payload)
    
    if resp['status'] == 200:
        print(f"   ✅ Status 200 OK")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_create_bulk_ky_phase():
    """Test POST /api/pdt/quan-ly-hoc-ky/ky-phase/bulk"""
    print("Testing Create Bulk Ky Phase...")
    
    # 1. Get Semester ID
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Create Phases
    payload = {
        "hocKyId": hoc_ky_id,
        "hocKyStartAt": "2023-10-01",
        "hocKyEndAt": "2024-02-01",
        "phases": [
            {
                "phase": "ghi_danh",
                "startAt": "2023-10-01",
                "endAt": "2023-10-15"
            },
            {
                "phase": "dang_ky_hoc_phan",
                "startAt": "2023-10-16",
                "endAt": "2023-10-31"
            }
        ]
    }
    
    resp = make_request(f"{BASE_URL}/pdt/quan-ly-hoc-ky/ky-phase/bulk", method="POST", data=payload)
    
    if resp['status'] == 200:
        data = resp['data']['data']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Created {len(data)} phases")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

def test_course_proposal():
    """Test GET/PATCH /api/pdt/de-xuat-hoc-phan"""
    print("Testing Course Proposal...")
    
    # 1. Get Proposals
    resp = make_request(f"{BASE_URL}/pdt/de-xuat-hoc-phan")
    if not resp:
        print("❌ Request failed (None response)")
        return False
        
    if resp['status'] != 200:
        print(f"❌ Could not get proposals: {resp}")
        return False
        
    print(f"DEBUG: resp['data'] = {resp['data']}")
    proposals = resp['data'].get('data', [])
    print(f"   ✅ Got {len(proposals)} proposals")
    
    if len(proposals) > 0:
        proposal_id = proposals[0]['id']
        print(f"   Testing approval for proposal {proposal_id}")
        
        # 2. Approve Proposal
        payload = {"id": proposal_id}
        resp = make_request(f"{BASE_URL}/pdt/de-xuat-hoc-phan/duyet", method="PATCH", data=payload)
        
        if resp['status'] == 200:
             print(f"   ✅ Approved successfully")
        else:
             print(f"   ❌ Approval failed: {resp}")
             return False
             
    return True

def test_get_phases_by_hoc_ky():
    """Test GET /api/pdt/quan-ly-hoc-ky/ky-phase/{hocKyId}"""
    print("Testing Get Phases By Hoc Ky...")
    
    # 1. Get Semester ID
    resp = make_request(f"{BASE_URL}/hoc-ky-hien-hanh")
    if not resp or resp['status'] != 200:
        print(f"❌ Could not get current semester: {resp}")
        return False
        
    hoc_ky_id = resp['data']['data']['id']
    
    # 2. Get Phases
    resp = make_request(f"{BASE_URL}/pdt/quan-ly-hoc-ky/ky-phase/{hoc_ky_id}")
    
    if resp['status'] == 200:
        data = resp['data']['data']['phases']
        print(f"   ✅ Status 200 OK")
        print(f"   ✅ Got {len(data)} phases")
        return True
    else:
        print(f"   ❌ Unexpected status: {resp['status']}")
        print(f"   Response Data: {resp['data']}")
        return False

if __name__ == "__main__":
    print("Running Integration Tests for PDT...")
    success = True
    
    if not test_set_hoc_ky_hien_hanh():
        success = False
        print("❌ test_set_hoc_ky_hien_hanh FAIL")
    else:
        print("✅ test_set_hoc_ky_hien_hanh PASS")
        
    if not test_create_bulk_ky_phase():
        success = False
        print("❌ test_create_bulk_ky_phase FAIL")
    else:
        print("✅ test_create_bulk_ky_phase PASS")

    if not test_course_proposal():
        success = False
        print("❌ test_course_proposal FAIL")
    else:
        print("✅ test_course_proposal PASS")

    if not test_get_phases_by_hoc_ky():
        success = False
        print("❌ test_get_phases_by_hoc_ky FAIL")
    else:
        print("✅ test_get_phases_by_hoc_ky PASS")
        
    sys.exit(0 if success else 1)
