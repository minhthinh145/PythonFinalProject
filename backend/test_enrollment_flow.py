import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:8000/api"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0Mzg2NTA3LCJpYXQiOjE3NjQzODYyMDcsImp0aSI6IjE0YTM2YTIzZDdhYjRiMmZiYzY4ODdjOTRiMzljZWQxIiwidXNlcl9pZCI6ImE0ZjhhNzAyLTU0ZDgtNGZiNy1iNTgxLWU2OWE1OTkxZTk5NCIsInJvbGUiOiJzaW5oX3ZpZW4ifQ.3MaJw7WCDCq1MyHxay-gnzSLXpQ-HfxCevXYoume7us"

def request(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    if data:
        data = json.dumps(data).encode('utf-8')
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            return status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": "Non-JSON response", "body": body[:200]}
    except Exception as e:
        print(f"Error: {e}")
        return 500, None

def run_test():
    print("=== STARTING ENROLLMENT TEST ===")
    
    # 1. Get Semesters
    print("\n1. Getting Semesters...")
    status, res = request("GET", "hoc-ky-nien-khoa")
    print(f"Status: {status}")
    if status != 200 or not res.get('isSuccess'):
        print("Failed to get semesters")
        print(res)
        return
    
    hoc_ky_list = res.get('data', [])
    if not hoc_ky_list:
        print("No semesters found")
        return
        
    hoc_ky_id = hoc_ky_list[0]['id']
    print(f"Using HocKy ID: {hoc_ky_id}")
    
    # 2. Check Status
    print("\n2. Checking Registration Status...")
    status, res = request("GET", "sv/check-ghi-danh")
    print(f"Status: {status}")
    # print(res)
    
    # 3. Get Subjects
    print(f"\n3. Getting Subjects for HocKy {hoc_ky_id}...")
    status, res = request("GET", f"sv/mon-hoc-ghi-danh")
    print(f"Status: {status}")
    
    subjects = res.get('data', [])
    if not subjects:
        print("No subjects found")
        return
        
    # Pick a subject to register
    subject = subjects[0]
    mon_hoc_id = subject['id']
    print(f"Picking Subject: {subject['tenMonHoc']} ({mon_hoc_id})")
    
    # 4. Register Subject
    print(f"\n4. Registering Subject {mon_hoc_id}...")
    status, res = request("POST", "sv/ghi-danh", {"monHocId": mon_hoc_id})
    print(f"Status: {status}")
    print(res)
    
    if status != 200 and res.get('errorCode') != 'ALREADY_REGISTERED':
        print("Failed to register")
        # return # Continue to check list
        
    # 5. Verify Registration
    print("\n5. Verifying Registration...")
    status, res = request("GET", "sv/ghi-danh/my")
    print(f"Status: {status}")
    
    my_subjects = res.get('data', [])
    registered_subject = next((s for s in my_subjects if s['monHocId'] == mon_hoc_id), None)
    
    if registered_subject:
        print("SUCCESS: Subject found in registered list")
        ghi_danh_id = registered_subject['ghiDanhId']
        print(f"GhiDanh ID: {ghi_danh_id}")
        
        # 6. Cancel Registration
        print(f"\n6. Canceling Registration {ghi_danh_id}...")
        status, res = request("DELETE", "sv/ghi-danh", {"ghiDanhIds": [ghi_danh_id]})
        print(f"Status: {status}")
        print(res)
        
        # 7. Verify Cancellation
        print("\n7. Verifying Cancellation...")
        status, res = request("GET", "sv/ghi-danh/my")
        my_subjects = res.get('data', [])
        found = any(s['monHocId'] == mon_hoc_id for s in my_subjects)
        if not found:
            print("SUCCESS: Subject removed from registered list")
        else:
            print("FAILURE: Subject still in registered list")
            
    else:
        print("FAILURE: Subject NOT found in registered list")

if __name__ == "__main__":
    run_test()
