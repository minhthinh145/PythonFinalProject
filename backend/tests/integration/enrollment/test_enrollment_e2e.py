import os
import sys
import django
import json
import urllib.request
import urllib.error
import uuid
from datetime import datetime, timedelta
import pytest

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
django.setup()

from infrastructure.persistence.models import (
    HocKy, MonHoc, Khoa, Users, GiangVien, NienKhoa, 
    LopHocPhan, HocPhan, DotDangKy, SinhVien, GhiDanhHocPhan
)
from core.utils.password import PasswordService
from django.utils import timezone

BASE_URL = "http://localhost:8000/api"

def login(username, password):
    url = f"{BASE_URL}/auth/login"
    headers = {'Content-Type': 'application/json'}
    data = {"tenDangNhap": username, "matKhau": password}
    
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
        # Cleanup existing test data
        from infrastructure.persistence.models import TaiKhoan
        try:
            TaiKhoan.objects.using('neon').filter(ten_dang_nhap="sv_test_enrollment").delete()
            Users.objects.using('neon').filter(email="svtest@test.com").delete()
        except Exception:
            pass

        # Create NienKhoa
        nk, _ = NienKhoa.objects.using('neon').get_or_create(
            ten_nien_khoa="2025-2026",
            defaults={'id': uuid.uuid4()}
        )
        
        # Create HocKy
        hk, _ = HocKy.objects.using('neon').get_or_create(
            ten_hoc_ky="Học kỳ 1",
            id_nien_khoa=nk,
            defaults={'id': uuid.uuid4(), 'so_thu_tu': 1}
        )
        
        # Create Khoa
        khoa, _ = Khoa.objects.using('neon').get_or_create(
            ma_khoa="CNTT_TEST",
            defaults={'id': uuid.uuid4(), 'ten_khoa': "Khoa CNTT Test"}
        )
        
        # Create TaiKhoan
        from infrastructure.persistence.models import TaiKhoan
        tk, _ = TaiKhoan.objects.using('neon').get_or_create(
            ten_dang_nhap="sv_test_enrollment",
            defaults={
                'id': uuid.uuid4(),
                'mat_khau': PasswordService.hash_password("123456"),
                'loai_tai_khoan': 'sinh_vien',
                'trang_thai_hoat_dong': True,
                'ngay_tao': timezone.now()
            }
        )

        # Create User & SinhVien
        user, _ = Users.objects.using('neon').get_or_create(
            email="svtest@test.com",
            defaults={
                'id': uuid.uuid4(),
                'ho_ten': "Sinh Vien Test",
                'tai_khoan': tk
            }
        )
        # Ensure password is set correctly if created previously without hashing (though here we assume plain text for test env or handled by auth)
        # For this test, we assume auth uses plain text or we'd need to hash it. 
        # Given previous tests, it seems we might need to handle password hashing if auth system requires it.
        # But let's try plain first as per previous successful logins in other tests.
        
        sv, _ = SinhVien.objects.using('neon').get_or_create(
            ma_so_sinh_vien="SV001_TEST",
            defaults={
                'id': user, 
                'khoa': khoa,
                'ngay_nhap_hoc': timezone.now().date()
            }
        )
        
        # Create MonHoc
        mh, _ = MonHoc.objects.using('neon').get_or_create(
            ma_mon="MH001_TEST",
            defaults={
                'id': uuid.uuid4(),
                'ten_mon': "Mon Hoc Test",
                'so_tin_chi': 3,
                'khoa': khoa
            }
        )
        
        # Create HocPhan
        # Ensure it is OPEN
        hp, _ = HocPhan.objects.using('neon').get_or_create(
            mon_hoc=mh,
            id_hoc_ky=hk,
            defaults={
                'id': uuid.uuid4(),
                'so_lop': 1,
                'trang_thai_mo': True # Important!
            }
        )
        if not hp.trang_thai_mo:
            hp.trang_thai_mo = True
            hp.save()
        

        # Create DotGhiDanh
        now = timezone.now()
        dot, _ = DotDangKy.objects.using('neon').get_or_create(
            hoc_ky=hk,
            khoa=khoa,
            loai_dot='ghi_danh',
            defaults={
                'id': uuid.uuid4(),
                'thoi_gian_bat_dau': now - timedelta(days=1),
                'thoi_gian_ket_thuc': now + timedelta(days=1),
                'is_check_toan_truong': False
            }
        )
        
        # Clear existing enrollment if any
        GhiDanhHocPhan.objects.using('neon').filter(sinh_vien_id=user.id, hoc_phan_id=hp.id).delete()

        return sv, hp, hk
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        return None, None, None, None

@pytest.mark.django_db(databases=['default', 'neon'])
def test_enrollment_flow():
    print("Testing Enrollment Flow...")
    
    # 1. Setup Data
    sv, hp, hk = create_test_data()
    if not sv:
        print("❌ Failed to create test data")
        sys.exit(1)
        
    print(f"   Created data: SV={sv.ma_so_sinh_vien}, HP={hp.id}")
    
    # 2. Login
    token = login("sv_test_enrollment", "123456")
    if not token:
        print("❌ Login failed. Check user creation/password.")
        sys.exit(1)
        
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # 3. Get Available Courses (Mon Hoc Ghi Danh)
    url_get = f"{BASE_URL}/sv/mon-hoc-ghi-danh?hocKyId={hk.id}"
    req = urllib.request.Request(url_get, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            # Verify success
            if data.get('isSuccess') or data.get('success'):
                 print("   ✅ Available courses fetched.")
            else:
                 print(f"   ❌ Failed to fetch courses: {data}")
    except Exception as e:
        print(f"❌ Failed to get available courses: {e}")
        sys.exit(1)

    # 4. Enroll (Ghi Danh)
    print("   Attempting to enroll...")
    url_enroll = f"{BASE_URL}/sv/ghi-danh"
    data_enroll = {
        "monHocId": str(hp.id) # Use monHocId as per use case
    }
    
    req = urllib.request.Request(url_enroll, data=json.dumps(data_enroll).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('isSuccess') or data.get('success'):
                print("   ✅ Enrollment successful.")
            else:
                print(f"   ❌ Enrollment failed: {data}")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error Enroll: {e.code} - {e.read().decode('utf-8')}")
        sys.exit(1)

    # 5. Verify Enrollment (My Courses)
    print("   Verifying enrollment...")
    url_my = f"{BASE_URL}/sv/ghi-danh/my"
    req = urllib.request.Request(url_my, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('data', [])
            # Check if hp.id is in items
            found = False
            ghi_danh_id = None
            for item in items:
                # Item structure depends on GetDanhSachDaGhiDanhUseCase
                # Likely has hocPhanId or id
                if str(item.get('monHocId')) == str(hp.id) or str(item.get('id')) == str(hp.id):
                    found = True
                    ghi_danh_id = item.get('ghiDanhId')
                    break
            
            if found:
                print(f"   ✅ Course found in My Enrollments. GhiDanhID: {ghi_danh_id}")
            else:
                print(f"   ❌ Course NOT found in My Enrollments. Data: {items}")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to verify enrollment: {e}")
        sys.exit(1)

    # 6. Cancel Enrollment
    print("   Cancelling enrollment...")
    if not ghi_danh_id:
        print("❌ Cannot cancel, ghiDanhId not found")
        sys.exit(1)
        
    url_cancel = f"{BASE_URL}/sv/ghi-danh"
    data_cancel = {
        "ghiDanhIds": [ghi_danh_id]
    }
    req = urllib.request.Request(url_cancel, data=json.dumps(data_cancel).encode('utf-8'), headers=headers, method='DELETE')
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('isSuccess') or data.get('success'):
                print("   ✅ Cancellation successful.")
            else:
                print(f"   ❌ Cancellation failed: {data}")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to cancel enrollment: {e}")
        sys.exit(1)

    print("✅ TEST PASSED")

if __name__ == "__main__":
    test_enrollment_flow()
