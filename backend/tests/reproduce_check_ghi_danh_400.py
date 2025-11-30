import urllib.request
import json
import urllib.error

BASE_URL = "http://localhost:8000/api"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0NDgzMzI1LCJpYXQiOjE3NjQzOTY5MjUsImp0aSI6IjM1MDFjNWE4OTQ1YjRmMGNiY2U1MGYzNWY4MTM0ODQ0IiwidXNlcl9pZCI6ImE0ZjhhNzAyLTU0ZDgtNGZiNy1iNTgxLWU2OWE1OTkxZTk5NCIsInJvbGUiOiJzaW5oX3ZpZW4ifQ.i0SYhFKZ9-pnuexnKZbAc8TRs99ek-PCbzlKzuGHi2I"

def check_ghi_danh():
    url = f"{BASE_URL}/sv/check-ghi-danh"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {TOKEN}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"✅ Status: {response.status}")
            print(f"✅ Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_ghi_danh()
