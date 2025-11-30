"""
Integration test for /api/hoc-ky-hien-hanh endpoint

Tests the complete flow from HTTP request to database query
"""
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000/api"

# Get a valid token (reuse from previous tests)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0NDgzMzI1LCJpYXQiOjE3NjQzOTY5MjUsImp0aSI6IjM1MDFjNWE4OTQ1YjRmMGNiY2U1MGYzNWY4MTM0ODQ0IiwidXNlcl9pZCI6ImE0ZjhhNzAyLTU0ZDgtNGZiNy1iNTgxLWU2OWE1OTkxZTk5NCIsInJvbGUiOiJzaW5oX3ZpZW4ifQ.i0SYhFKZ9-pnuexnKZbAc8TRs99ek-PCbzlKzuGHi2I"

def test_hoc_ky_hien_hanh():
    """Test GET /api/hoc-ky-hien-hanh"""
    print("=" * 60)
    print("INTEGRATION TEST: GET /api/hoc-ky-hien-hanh")
    print("=" * 60)
    
    url = f"{BASE_URL}/hoc-ky-hien-hanh"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            data = json.loads(body)
            
            print(f"✅ Status: {status}")
            print(f"✅ Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Assertions
            assert status == 200, f"Expected 200, got {status}"
            assert data['isSuccess'] is True or data['isSuccess'] is False, "Missing isSuccess"
            
            if data['isSuccess'] and data['data']:
                assert 'id' in data['data'], "Missing id in data"
                assert 'tenHocKy' in data['data'], "Missing tenHocKy"
                assert 'maHocKy' in data['data'], "Missing maHocKy"
                assert 'nienKhoa' in data['data'], "Missing nienKhoa"
                assert 'ngayBatDau' in data['data'], "Missing ngayBatDau"
                assert 'ngayKetThuc' in data['data'], "Missing ngayKetThuc"
                print("✅ All fields present in response")
            else:
                print("ℹ️  No current semester found (this is OK)")
            
            return True
            
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8')
        print(f"❌ HTTP Error {status}")
        print(f"Response: {body}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_danh_sach_nganh():
    """Test GET /api/dm/nganh"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST: GET /api/dm/nganh")
    print("=" * 60)
    
    url = f"{BASE_URL}/dm/nganh"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            data = json.loads(body)
            
            print(f"✅ Status: {status}")
            print(f"✅ Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            
            # Assertions
            assert status == 200, f"Expected 200, got {status}"
            assert data['isSuccess'] is True, "Should be success"
            assert isinstance(data['data'], list), "Data should be a list"
            
            if len(data['data']) > 0:
                first_item = data['data'][0]
                assert 'id' in first_item, "Missing id"
                assert 'tenNganh' in first_item, "Missing tenNganh"
                print(f"✅ Found {len(data['data'])} programs")
            
            return True
            
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8')
        print(f"❌ HTTP Error {status}")
        print(f"Response: {body}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting Common API Integration Tests\n")
    
    results = []
    
    results.append(("hoc-ky-hien-hanh", test_hoc_ky_hien_hanh()))
    results.append(("danh-sach-nganh", test_danh_sach_nganh()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    exit(0 if all_passed else 1)
