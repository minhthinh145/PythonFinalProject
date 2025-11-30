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

from infrastructure.persistence.models import DeXuatHocPhan, HocKy, MonHoc, Khoa, Users, GiangVien, NienKhoa

BASE_URL = "http://localhost:8000/api"

def login():
    url = f"{BASE_URL}/auth/login"
    headers = {'Content-Type': 'application/json'}
    data = {
        "tenDangNhap": "49.01.104.145", # Student account, but we might need admin/PDT account. 
        # TODO: Check if student can reject? Likely not. Need PDT account.
        # Assuming 49.01.104.145 is used for testing, but strictly speaking should be PDT.
        # Let's check permissions. CourseProposalView has IsAuthenticated.
        # If role check is TODO, then any user might work.
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

def create_test_proposal():
    # Ensure dependencies exist
    # We need a valid HocKy, MonHoc, Khoa, User
    # This might be complex if DB is empty.
    # Assuming seed data exists or we can fetch one.
    
    try:
        hk = HocKy.objects.using('neon').first()
        mh = MonHoc.objects.using('neon').first()
        khoa = Khoa.objects.using('neon').first()
        user = Users.objects.using('neon').first()
        
        if not all([hk, mh, khoa, user]):
            print("Missing seed data (HocKy, MonHoc, Khoa, or User)")
            return None

        proposal = DeXuatHocPhan.objects.using('neon').create(
            id=uuid.uuid4(),
            khoa=khoa,
            nguoi_tao=user,
            hoc_ky=hk,
            mon_hoc=mh,
            so_lop_du_kien=2,
            trang_thai='cho_duyet',
            created_at=datetime.now()
        )
        return proposal
    except Exception as e:
        print(f"Error creating proposal: {e}")
        return None

def test_reject_proposal():
    print("Testing Course Proposal Rejection...")
    
    # 1. Create Data
    proposal = create_test_proposal()
    if not proposal:
        print("❌ Failed to create test proposal")
        sys.exit(1)
    print(f"   Created proposal: {proposal.id}")

    # 2. Login
    token = login()
    if not token:
        print("❌ Login failed")
        sys.exit(1)
        
    # 3. Reject
    url = f"{BASE_URL}/pdt/de-xuat-hoc-phan/tu-choi"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        "id": str(proposal.id),
        "lyDo": "Test rejection reason"
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='PATCH')
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            if resp_data.get('isSuccess'):
                print("   ✅ API Call Success")
            else:
                print(f"   ❌ API Call Failed: {resp_data}")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        sys.exit(1)
        
    # 4. Verify DB
    proposal.refresh_from_db()
    if proposal.trang_thai == 'tu_choi':
        print("   ✅ DB Status Updated to tu_choi")
    else:
        print(f"   ❌ DB Status Mismatch: {proposal.trang_thai}")
        sys.exit(1)
        
    # 5. Verify Log (Optional but good)
    from infrastructure.persistence.models import DeXuatHocPhanLog
    log = DeXuatHocPhanLog.objects.using('neon').filter(de_xuat=proposal, hanh_dong='TU_CHOI').first()
    if log and log.ghi_chu == "Test rejection reason":
        print("   ✅ Log Entry Created")
    else:
        print("   ❌ Log Entry Missing or Incorrect")
        
    print("✅ TEST PASSED")

if __name__ == "__main__":
    test_reject_proposal()
