# 🧪 HƯỚNG DẪN TEST DỰ ÁN DKHP - TỪ A → Z

## 📋 MỤC LỤC

1. [Cấu trúc Test](#1-cấu-trúc-test)
2. [Cài đặt môi trường](#2-cài-đặt-môi-trường)
3. [Chạy Unit Tests](#3-chạy-unit-tests)
4. [Chạy Integration Tests](#4-chạy-integration-tests)
5. [Test API thủ công](#5-test-api-thủ-công)
6. [CI/CD Script](#6-cicd-script)
7. [Debug Test Failures](#7-debug-test-failures)
8. [Coding Convention](#8-coding-convention)

---

## 1. CẤU TRÚC TEST

```
tests/
├── unit/                           # Unit tests - Mock dependencies
│   ├── course_registration/        # SV module
│   │   ├── test_dang_ky_hoc_phan_use_case.py
│   │   ├── test_get_danh_sach_lop_hoc_phan_use_case.py
│   │   ├── test_get_tkb_weekly_use_case.py
│   │   └── ...
│   ├── pdt/                        # PDT module
│   │   ├── test_get_de_xuat_hoc_phan_use_case.py
│   │   └── ...
│   ├── gv/                         # GV module
│   │   ├── test_get_lop_hoc_phan_gv.py
│   │   └── ...
│   └── auth/                       # Auth module
│       └── test_auth_use_case.py
│
├── integration/                    # Integration tests - Real DB
│   ├── pdt/
│   │   └── test_course_proposal_reject_e2e.py
│   └── sv/
│       └── test_enrollment_flow.py
│
└── conftest.py                     # Pytest fixtures
```

---

## 2. CÀI ĐẶT MÔI TRƯỜNG

### 2.1. Tạo Virtual Environment

```bash
cd /mnt/data/PythonProject/backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows
```

### 2.2. Cài Dependencies

```bash
pip install -r requirements.txt
```

### 2.3. File `.env.test` (Test environment)

```dotenv
# Đã có sẵn trong project
DEBUG=True
DATABASE_URL=sqlite:///./test_db.sqlite3
```

---

## 3. CHẠY UNIT TESTS

### 3.1. Chạy tất cả unit tests

```bash
cd /mnt/data/PythonProject/backend
pytest tests/unit/ -v
```

### 3.2. Chạy test module cụ thể

```bash
# Test SV module
pytest tests/unit/course_registration/ -v

# Test PDT module
pytest tests/unit/pdt/ -v

# Test GV module
pytest tests/unit/gv/ -v

# Test Auth module
pytest tests/unit/auth/ -v
```

### 3.3. Chạy một test file cụ thể

```bash
pytest tests/unit/course_registration/test_dang_ky_hoc_phan_use_case.py -v
```

### 3.4. Chạy một test function cụ thể

```bash
pytest tests/unit/course_registration/test_dang_ky_hoc_phan_use_case.py::test_dang_ky_success -v
```

### 3.5. Xem coverage

```bash
pytest tests/unit/ --cov=application --cov-report=html
# Mở htmlcov/index.html để xem chi tiết
```

---

## 4. CHẠY INTEGRATION TESTS

### 4.1. Chạy integration tests (cần real DB)

```bash
# Cần set DATABASE_URL trong .env trỏ đến test database
pytest tests/integration/ -v --ds=DKHPHCMUE.settings
```

### 4.2. Skip integration tests

```bash
pytest tests/ -v --ignore=tests/integration/
```

---

## 5. TEST API THỦ CÔNG

### 5.1. Lấy Token

```bash
# Sử dụng script get_token.py
cd /mnt/data/PythonProject/backend
python get_token.py

# Hoặc dùng curl:
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sv001", "password": "123456"}'
```

### 5.2. Test API với Token

```bash
# Lưu token vào biến
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Test GET
curl -X GET http://localhost:8000/api/sv/lop-hoc-phan \
  -H "Authorization: Bearer $TOKEN"

# Test POST
curl -X POST http://localhost:8000/api/sv/dang-ky-hoc-phan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lopHocPhanId": "uuid-here"}'
```

### 5.3. Test với HTTPie (dễ đọc hơn curl)

```bash
# Cài đặt
pip install httpie

# Test
http GET localhost:8000/api/sv/lop-hoc-phan Authorization:"Bearer $TOKEN"
```

### 5.4. Test với Python Script

```python
# test_api_manual.py
import requests

BASE_URL = "http://localhost:8000/api"

# Login
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "sv001",
    "password": "123456"
})
token = resp.json()["data"]["token"]

# Test API
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(f"{BASE_URL}/sv/lop-hoc-phan", headers=headers)
print(resp.json())
```

---

## 6. CI/CD SCRIPT

### 6.1. Sử dụng full_ci_cd.py

```bash
cd /mnt/data/PythonProject/backend
python full_ci_cd.py
```

### 6.2. Nội dung full_ci_cd.py

Script thực hiện:

1. ✅ Lint code với flake8 (optional)
2. ✅ Chạy unit tests
3. ✅ Check coverage
4. ✅ Build Docker image (optional)
5. ✅ Deploy (optional)

### 6.3. Tích hợp GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/unit/ -v
```

---

## 7. DEBUG TEST FAILURES

### 7.1. Xem output chi tiết

```bash
pytest tests/unit/ -v --tb=long
```

### 7.2. Dừng ở test fail đầu tiên

```bash
pytest tests/unit/ -v -x
```

### 7.3. Debug với pdb

```bash
pytest tests/unit/ -v --pdb
```

### 7.4. Print debug info

```python
# Trong test file
def test_something():
    result = some_function()
    print(f"DEBUG: result = {result}")  # Hiện với -s flag
    assert result.isSuccess
```

```bash
pytest tests/unit/file.py -v -s  # -s để hiện print
```

### 7.5. Common Errors & Solutions

| Error                        | Solution                                 |
| ---------------------------- | ---------------------------------------- |
| `ModuleNotFoundError`        | Check PYTHONPATH hoặc thêm `__init__.py` |
| `Database connection failed` | Check `.env` và database status          |
| `Mock not working`           | Check mock path (phải mock ở nơi import) |
| `Fixture not found`          | Check `conftest.py` location             |

---

## 8. CODING CONVENTION

### 8.1. Test File Naming

```
test_<module>_<feature>.py
# Ví dụ: test_dang_ky_hoc_phan_use_case.py
```

### 8.2. Test Function Naming

```python
def test_<action>_<scenario>_<expected_result>():
    pass

# Ví dụ:
def test_dang_ky_success():
    pass

def test_dang_ky_when_class_full_should_return_error():
    pass
```

### 8.3. Test Structure (AAA Pattern)

```python
def test_dang_ky_success():
    # Arrange - Setup data & mocks
    mock_repo = MagicMock()
    mock_repo.find_by_id.return_value = mock_lop
    use_case = DangKyHocPhanUseCase(mock_repo)

    # Act - Execute
    result = use_case.execute(sinh_vien_id, lop_hoc_phan_id)

    # Assert - Verify
    assert result.isSuccess is True
    assert result.data is not None
```

### 8.4. Mock Best Practices

```python
from unittest.mock import MagicMock, patch

# Mock repository
@patch('application.use_cases.DangKyRepository')
def test_something(mock_repo_class):
    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo
    mock_repo.find_by_id.return_value = some_data

    # Test...

# Mock external service
@patch('infrastructure.services.PaymentService.process')
def test_payment(mock_process):
    mock_process.return_value = {"status": "success"}

    # Test...
```

---

## 📊 QUICK REFERENCE

### Pytest Commands

| Command               | Description                |
| --------------------- | -------------------------- |
| `pytest`              | Chạy tất cả tests          |
| `pytest -v`           | Verbose output             |
| `pytest -s`           | Show print statements      |
| `pytest -x`           | Stop on first failure      |
| `pytest -k "pattern"` | Run tests matching pattern |
| `pytest --tb=short`   | Shorter traceback          |
| `pytest --cov=app`    | Show coverage              |

### Test Markers

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.skip(reason="Not implemented")
def test_future_feature():
    pass

@pytest.mark.skipif(condition, reason="...")
def test_conditional():
    pass
```

```bash
# Run only marked tests
pytest -m slow

# Skip marked tests
pytest -m "not slow"
```

---

## 🔗 ENDPOINTS CHÍNH CẦN TEST

### Auth Module

```
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
POST /api/auth/change-password
POST /api/auth/forgot-password
POST /api/auth/reset-password
```

### SV Module

```
GET  /api/sv/check-phase-dang-ky
GET  /api/sv/lop-hoc-phan
GET  /api/sv/lop-da-dang-ky
POST /api/sv/dang-ky-hoc-phan
POST /api/sv/huy-dang-ky-hoc-phan
POST /api/sv/chuyen-lop-hoc-phan
GET  /api/sv/tkb
GET  /api/sv/tkb-weekly
GET  /api/sv/hoc-phi
GET  /api/sv/tai-lieu/lop/:id
```

### GV Module

```
GET  /api/gv/lop-hoc-phan
GET  /api/gv/lop-hoc-phan/:id
GET  /api/gv/tkb
POST /api/gv/upload-tai-lieu
```

### TLK Module

```
GET  /api/tlk/mon-hoc
GET  /api/tlk/giang-vien
GET  /api/tlk/phong-hoc
GET  /api/tlk/phong-hoc/available
GET  /api/tlk/lop-hoc-phan/get-hoc-phan/:hocKyId
POST /api/tlk/de-xuat-hoc-phan
GET  /api/tlk/de-xuat-hoc-phan
POST /api/tlk/thoi-khoa-bieu
POST /api/tlk/thoi-khoa-bieu/batch
```

### PDT Module

```
GET    /api/pdt/sinh-vien
POST   /api/pdt/sinh-vien
PUT    /api/pdt/sinh-vien/:id
DELETE /api/pdt/sinh-vien/:id
GET    /api/pdt/de-xuat-hoc-phan
PATCH  /api/pdt/de-xuat-hoc-phan/duyet
PATCH  /api/pdt/de-xuat-hoc-phan/tu-choi
POST   /api/tuition/compute
```

---

## ✅ CHECKLIST TRƯỚC KHI COMMIT

- [ ] Chạy `pytest tests/unit/ -v` - Tất cả PASS
- [ ] Chạy `flake8 .` - Không có linting errors
- [ ] Test manual API với token
- [ ] Update documentation nếu cần
- [ ] Commit message rõ ràng

---

_Last updated: December 2024_
