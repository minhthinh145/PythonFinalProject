# 🚀 MIGRATION PLAN: Django Clean Architecture

## 📋 Phase 1: Foundation & Authentication (CURRENT)

### Step 1: Models Setup ✅

- [x] Generate models từ Neon DB
- [x] Copy models vào `infrastructure/persistence/models.py`
- [x] Configure database routing

### Step 2: Authentication Use Case 🎯 ✅

**Priority: HIGH | Complexity: LOW | Status: DONE**

#### Files cần tạo:

```
domain/
└── entities/
    └── user.py                 # User entity với business logic

application/
├── dtos/
│   ├── auth_dto.py            # LoginDTO, TokenDTO
├── ports/
│   ├── auth_repository.py     # IAuthRepository interface
│   └── token_service.py       # ITokenService interface
└── use_cases/
    ├── login_usecase.py       # LoginUseCase
    └── get_user_info_usecase.py

infrastructure/
├── persistence/
│   ├── models.py              # Django models (từ inspectdb)
│   └── auth_repository.py     # AuthRepository implementation
└── services/
    ├── jwt_service.py         # JWT token service
    └── password_service.py    # Bcrypt password hashing

presentation/
└── api/
    ├── serializers/
    │   └── auth_serializer.py # DRF serializers
    ├── views/
    │   └── auth_views.py      # API ViewSets
    └── urls/
        └── auth_urls.py       # URL routing

test-case/
├── unit/
│   ├── test_login_usecase.py
│   └── test_jwt_service.py
├── integration/
│   └── test_auth_repository.py
└── e2e/
    └── test_login_api.py
```

#### API Endpoints:

- POST `/api/auth/login` - Login và lấy JWT token
- POST `/api/auth/refresh` - Refresh token
- GET `/api/auth/me` - Get user info
- POST `/api/auth/logout` - Logout (blacklist token)

---

## 📋 Phase 2: Core Domain Models

### Step 3: Sinh Viên Module (NEXT)

- [ ] Entities: SinhVien
- [ ] Use cases: GetSinhVienInfo, UpdateProfile
- [ ] Test cases

### Step 4: Danh Mục (Master Data)

- [ ] GET /api/dm/khoa
- [ ] GET /api/dm/nganh
- [ ] GET /api/dm/nien-khoa

---

## 📋 Phase 3: Registration Flow

### Step 5: Ghi Danh (Enrollment)

- [ ] CheckPhaseGhiDanh
- [ ] GhiDanhMonHoc
- [ ] GetDanhSachGhiDanh

### Step 6: Đăng Ký Học Phần

- [ ] CheckPhaseDangKy
- [ ] DangKyHocPhan
- [ ] HuyDangKyHocPhan
- [ ] ChuyenLopHocPhan

### Step 7: Thời Khóa Biểu

- [ ] GetTKBSinhVien
- [ ] GetTKBWeekly
- [ ] CheckXungDot

---

## 📋 Phase 4: Advanced Features

### Step 8: Học Phí (Tuition)

- [ ] ComputeTuition
- [ ] GetTuitionDetails

### Step 9: Payment

- [ ] VNPay Integration
- [ ] MoMo Integration
- [ ] IPN Handler

### Step 10: PDT Module

- [ ] CRUD Sinh viên
- [ ] CRUD Giảng viên
- [ ] Quản lý học kỳ & Phase
- [ ] Báo cáo thống kê

---

## 🎯 Current Focus: Authentication Use Case

### Test-Driven Development Flow:

1. ✍️ Write test case (RED)
2. ✅ Implement code (GREEN)
3. ♻️ Refactor (REFACTOR)
4. 🔄 Repeat

### Testing Strategy:

- **Unit Tests**: Test use cases, services in isolation
- **Integration Tests**: Test repository với real DB
- **E2E Tests**: Test API endpoints với DRF test client

---

## 📦 Dependencies cần thêm:

```txt
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.3.0
django-cors-headers>=4.3.1
pytest>=7.4.0
pytest-django>=4.5.0
factory-boy>=3.3.0      # Test fixtures
faker>=20.0.0           # Fake data
```
