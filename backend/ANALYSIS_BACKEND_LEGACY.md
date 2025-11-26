# 🏗️ PHÂN TÍCH CLEAN ARCHITECTURE - BACKEND CŨ (Node.js/TypeScript)

## 📊 TỔNG QUAN HỆ THỐNG

### Công nghệ stack:

- **Framework**: Express.js + TypeScript
- **ORM**: Prisma (PostgreSQL)
- **Database**: PostgreSQL (Neon) + MongoDB (tài liệu)
- **DI Container**: InversifyJS
- **Architecture Pattern**: Clean Architecture + DDD

---

## 🎯 CẤU TRÚC CLEAN ARCHITECTURE

### 1. **Domain Layer** (Lõi nghiệp vụ - Độc lập nhất)

```
src/domain/
├── entities/              # Business Entities
│   ├── SinhVien.entity.ts
│   ├── HocKy.entity.ts
│   ├── Payment.ts
│   └── KyPhase.entity.ts
├── value-objects/         # Value Objects (immutable)
├── services/              # Domain Services
└── errors/                # Domain Exceptions
```

**Đặc điểm:**

- Pure TypeScript classes
- Business logic & validation
- Không phụ thuộc framework/database
- Ví dụ: `SinhVien.entity.ts` có methods: `create()`, `update()`, `isValid()`

---

### 2. **Application Layer** (Use Cases - Business Logic)

```
src/application/
├── use-cases/
│   ├── qlSinhVienPDT/
│   │   ├── crud/
│   │   │   ├── CreateSinhVien.usecase.ts
│   │   │   ├── UpdateSinhVien.usecase.ts
│   │   │   ├── DeleteSinhVien.usecase.ts
│   │   │   └── ListSinhVien.usecase.ts
│   │   └── import/
│   │       └── ImportSinhVien.usecase.ts
│   ├── payment/
│   │   ├── ProcessIPN.usecase.ts
│   │   └── GetPaymentStatus.usecase.ts
│   ├── tuition/
│   │   ├── ComputeTuition.usecase.ts
│   │   └── CalculateTuitionForSemester.usecase.ts
│   └── baoCaoThongKe/
│       ├── GetOverview.usecase.ts
│       └── ExportBaoCao.usecase.ts
├── ports/                 # Interfaces (Dependency Inversion)
│   ├── IUnitOfWork
│   ├── ISinhVienRepository
│   └── IPasswordHasher
└── dtos/                  # Data Transfer Objects
    ├── CreateSinhVien.dto.ts
    └── UpdateSinhVien.dto.ts
```

**Đặc điểm:**

- Mỗi use case = 1 business action
- Inject dependencies qua constructor (InversifyJS)
- Return `ServiceResult<T>` (success/failure pattern)
- Ví dụ pattern:

```typescript
@injectable()
export class UpdateSinhVienUseCase {
  constructor(
    @inject(TYPES.IUnitOfWork) private unitOfWork: IUnitOfWork,
    @inject(TYPES.IPasswordHasher) private passwordHasher: IPasswordHasher
  ) {}

  async execute(
    id: string,
    input: UpdateSinhVienInputDTO
  ): Promise<ServiceResult<any>> {
    // 1. Validation
    // 2. Business logic
    // 3. Transaction
    // 4. Return result
  }
}
```

---

### 3. **Infrastructure Layer** (Implementation Details)

```
src/infrastructure/
├── persistence/           # Database implementations
│   ├── PrismaSinhVienRepository.ts
│   ├── PrismaHocKyRepository.ts
│   └── PrismaUnitOfWork.ts
├── services/              # External services
│   ├── BcryptPasswordHasher.ts
│   ├── VNPayService.ts
│   └── MoMoService.ts
├── di/                    # Dependency Injection
│   ├── container.ts
│   └── types.ts           # Symbol definitions
├── external/              # 3rd party integrations
└── gateways/              # API gateways
```

**Đặc điểm:**

- Implement các interfaces từ Application Layer
- Prisma client wrapper
- External services (Payment, Email, etc.)

---

### 4. **Interface/Presentation Layer** (Adapter - HTTP)

```
src/
├── interface/
│   ├── controllers/       # Clean Architecture Controllers
│   │   ├── sinhvien/
│   │   │   └── SinhVien.controller.ts
│   │   └── tuition/
│   │       └── TuitionController.ts
│   └── routes/            # Clean Architecture Routes
│       ├── tuitionsv.routes.ts
│       └── sinh-vien.routes.ts
│
├── presentation/          # Alternative presentation layer
│   └── http/
│       ├── controllers/
│       └── routes/
│
└── modules/               # Feature-based routing (Legacy)
    ├── auth/
    ├── sv/                # Sinh viên
    │   ├── sv.router.ts
    │   └── sv_*_service.ts
    ├── pdt/               # Phòng đào tạo
    ├── gv/                # Giảng viên
    ├── tk/                # Trưởng khoa
    └── tlk/               # Trợ lý khoa
```

**Đặc điểm:**

- 2 kiểu routing:
  - `modules/` (legacy, feature-based)
  - `interface/` & `presentation/` (Clean Architecture)
- Controllers inject use cases
- Handle HTTP request/response
- Authentication middleware

---

## 📦 MODULES CHÍNH

### 1. **Authentication & Authorization**

```
modules/auth/
├── auth.router.ts         # Login, register
├── forgotPassword.router.ts
└── changePassword.router.ts
```

**Roles**:

- `sinh_vien` (Sinh viên)
- `phong_dao_tao` (PDT)
- `giang_vien` (GV)
- `truong_khoa` (TK)
- `tro_ly_khoa` (TLK)

---

### 2. **Sinh Viên Module** (`/api/sv`)

**Chức năng chính:**

```typescript
// GHI DANH (Enrollment)
GET  /api/sv/check-ghi-danh          // Check phase
GET  /api/sv/mon-hoc-ghi-danh        // Danh sách môn ghi danh
POST /api/sv/ghi-danh                // Ghi danh môn học
GET  /api/sv/ghi-danh/my             // Danh sách đã ghi danh

// ĐĂNG KÝ HỌC PHẦN (Course Registration)
GET  /api/sv/check-phase-dang-ky     // Check phase
GET  /api/sv/lop-hoc-phan            // Danh sách lớp (có filter)
GET  /api/sv/lop-da-dang-ky          // Lớp đã đăng ký
POST /api/sv/dang-ky-hoc-phan        // Đăng ký
POST /api/sv/huy-dang-ky-hoc-phan    // Hủy đăng ký
POST /api/sv/chuyen-lop-hoc-phan     // Chuyển lớp

// THỜI KHÓA BIỂU
GET  /api/sv/tkb                     // TKB của sinh viên
GET  /api/sv/tkb-weekly              // TKB theo tuần

// HỌC PHÍ
GET  /api/sv/hoc-phi                 // Chi tiết học phí
GET  /api/hoc-phi/chi-tiet           // Clean Architecture endpoint

// TÀI LIỆU
GET  /api/sv/tai-lieu/lop/:id        // Tài liệu của lớp
```

---

### 3. **PDT Module** (`/api/pdt`)

**Chức năng chính:**

```typescript
// QUẢN LÝ SINH VIÊN
GET    /api/pdt/sinh-vien            // Danh sách sinh viên (phân trang)
POST   /api/pdt/sinh-vien            // Tạo sinh viên
PUT    /api/pdt/sinh-vien/:id        // Cập nhật sinh viên
DELETE /api/pdt/sinh-vien/:id        // Xóa sinh viên
POST   /api/pdt/sinh-vien/import     // Import từ Excel

// QUẢN LÝ GIẢNG VIÊN
GET    /api/pdt/giang-vien
POST   /api/pdt/giang-vien
PUT    /api/pdt/giang-vien/:id
DELETE /api/pdt/giang-vien/:id

// QUẢN LÝ MÔN HỌC
GET    /api/pdt/mon-hoc
POST   /api/pdt/mon-hoc
PUT    /api/pdt/mon-hoc/:id
DELETE /api/pdt/mon-hoc/:id

// QUẢN LÝ HỌC KỲ & PHASE
GET    /api/pdt/quan-ly-hoc-ky/hien-hanh
POST   /api/pdt/quan-ly-hoc-ky/set-hien-hanh
GET    /api/pdt/quan-ly-hoc-ky/phases/:hocKyId
POST   /api/pdt/quan-ly-hoc-ky/phases/bulk

// ĐỢT ĐĂNG KÝ
GET    /api/pdt/dot-dang-ky/:hocKyId
PUT    /api/pdt/dot-dang-ky/:id

// ĐỀ XUẤT HỌC PHẦN (từ Trưởng Khoa)
GET    /api/pdt/de-xuat-hoc-phan
PATCH  /api/pdt/de-xuat-hoc-phan/duyet
PATCH  /api/pdt/de-xuat-hoc-phan/tu-choi

// HỌC PHÍ
POST   /api/tuition/compute          // Tính học phí cho sinh viên
GET    /api/chinh-sach-tin-chi
POST   /api/chinh-sach-tin-chi

// BÁO CÁO THỐNG KÊ
GET    /api/bao-cao/overview
GET    /api/bao-cao/dang-ky-theo-khoa
GET    /api/bao-cao/dang-ky-theo-nganh
GET    /api/bao-cao/tai-giang-vien
POST   /api/bao-cao/export
```

---

### 4. **Payment Module** (`/api/payment`)

**Clean Architecture Implementation:**

```typescript
// Use Cases
- ProcessIPNUseCase          // Xử lý IPN từ VNPay/MoMo
- GetPaymentStatusUseCase    // Lấy trạng thái thanh toán
- UnifiedIPNHandlerUseCase   // Unified handler cho nhiều gateway

// Endpoints
POST /api/payment/vnpay/ipn
POST /api/payment/momo/ipn
GET  /api/payment/status/:transactionId
```

---

### 5. **Tuition (Học phí) Module**

**Clean Architecture:**

```typescript
// Use Cases
-ComputeTuitionUseCase - // Tính học phí cho 1 SV
  CalculateTuitionForSemesterUseCase - // Tính học phí cả kỳ
  GetTuitionDetailsUseCase; // Chi tiết học phí

// Endpoints
POST / api / tuition / compute; // PDT tính học phí
GET / api / hoc - phi / chi - tiet; // SV xem học phí
```

---

## 🗄️ DATABASE SCHEMA (Prisma)

### Core Tables:

**1. Users & Roles:**

```prisma
tai_khoan (Accounts)
├── id
├── mat_khau (password hash)
├── vai_tro (role)
└── trang_thai_hoat_dong

users (User info)
├── id
├── ho_ten
├── email
├── tai_khoan_id
└── created_at

sinh_vien (extends users)
├── id (= users.id)
├── ma_so_sinh_vien
├── khoa_id
├── nganh_id
├── lop
└── khoa_hoc

giang_vien (extends users)
├── id (= users.id)
├── khoa_id
├── chuyen_mon
└── trinh_do
```

**2. Academic Structure:**

```prisma
nien_khoa (Academic Year)
└── hoc_ky[] (Semester)
    └── ky_phase[] (Phase: ghi_danh, dang_ky, huy_dang_ky)

mon_hoc (Subject)
└── hoc_phan[] (Course - per semester)
    └── lop_hoc_phan[] (Class)
        ├── giang_vien_id
        ├── phong_id
        ├── so_luong_toi_da
        ├── thoi_gian_hoc (JSON)
        └── dang_ky_hoc_phan[]
```

**3. Registration Flow:**

```prisma
// STEP 1: Ghi danh
ghi_danh_hoc_phan
├── sinh_vien_id
├── hoc_phan_id
└── trang_thai

// STEP 2: Đăng ký lớp
dang_ky_hoc_phan
├── sinh_vien_id
├── lop_hoc_phan_id
├── trang_thai (da_dang_ky, da_huy)
└── co_xung_dot (TKB conflict flag)

// STEP 3: Thời khóa biểu
dang_ky_tkb
├── sinh_vien_id
├── lop_hoc_phan_id
└── dang_ky_id
```

**4. Tuition:**

```prisma
chinh_sach_tin_chi (Policy)
├── hoc_ky_id
├── phi_moi_tin_chi
└── ngay_hieu_luc

hoc_phi (Student tuition)
├── sinh_vien_id
├── hoc_ky_id
├── tong_hoc_phi
├── trang_thai_thanh_toan
└── chi_tiet_hoc_phi[] (per class)
```

**5. Payment:**

```prisma
payment_transactions
├── id
├── sinh_vien_id
├── hoc_ky_id
├── amount
├── gateway (vnpay/momo)
├── status
└── transaction_code
```

---

## 🔄 BUSINESS FLOWS

### Flow 1: Đăng ký học phần

```
1. SV check phase đang mở (GET /check-phase-dang-ky)
2. SV xem danh sách lớp (GET /lop-hoc-phan)
3. SV đăng ký (POST /dang-ky-hoc-phan)
   ├── Validate: đã ghi danh?
   ├── Validate: lớp còn chỗ?
   ├── Validate: xung đột TKB?
   ├── Create dang_ky_hoc_phan
   ├── Create dang_ky_tkb
   └── Create lich_su_dang_ky
```

### Flow 2: Tính học phí

```
1. PDT tính học phí (POST /tuition/compute)
   ├── Lấy chinh_sach_tin_chi
   ├── Lấy dang_ky_hoc_phan của SV
   ├── Tính: tổng_học_phí = Σ(số_tín_chỉ × phí_tín_chỉ)
   ├── Tạo/Update hoc_phi
   └── Tạo chi_tiet_hoc_phi (per class)

2. SV xem học phí (GET /hoc-phi/chi-tiet)
```

### Flow 3: Thanh toán

```
1. SV request thanh toán → Create payment_transaction
2. Redirect to VNPay/MoMo
3. Gateway callback (POST /payment/vnpay/ipn)
   ├── Verify signature
   ├── Update payment_transaction
   └── Update hoc_phi.trang_thai_thanh_toan
```

---

## 🎨 DESIGN PATTERNS

### 1. **Repository Pattern**

```typescript
// Interface (Port)
interface ISinhVienRepository {
  findById(id: string): Promise<SinhVien | null>;
  findPaged(params): Promise<{ items; total }>;
  create(data): Promise<SinhVien>;
  update(id, data): Promise<SinhVien>;
}

// Implementation (Adapter)
class PrismaSinhVienRepository implements ISinhVienRepository {
  constructor(private prisma: PrismaClient) {}
  // ... implement methods using Prisma
}
```

### 2. **Unit of Work Pattern**

```typescript
interface IUnitOfWork {
  getSinhVienRepository(): ISinhVienRepository;
  getTaiKhoanRepository(): ITaiKhoanRepository;
  transaction<T>(fn: (tx) => Promise<T>): Promise<T>;
}
```

### 3. **Dependency Injection (InversifyJS)**

```typescript
// types.ts
export const TYPES = {
  QlSinhVienPDT: {
    IUnitOfWork: Symbol.for("QlSinhVienPDT.IUnitOfWork"),
    ISinhVienRepository: Symbol.for("..."),
    UpdateSinhVienUseCase: Symbol.for("..."),
  },
};

// container.ts
container.bind(TYPES.IUnitOfWork).to(PrismaUnitOfWork);
container.bind(TYPES.UpdateSinhVienUseCase).to(UpdateSinhVienUseCase);

// Usage
@injectable()
class UpdateSinhVienUseCase {
  constructor(@inject(TYPES.IUnitOfWork) private uow: IUnitOfWork) {}
}
```

### 4. **Service Result Pattern**

```typescript
type ServiceResult<T> = {
  isSuccess: boolean;
  message: string;
  data?: T;
  errorCode?: string;
};

// Usage
return ServiceResultBuilder.success("OK", data);
return ServiceResultBuilder.failure("Error", "ERROR_CODE");
```

---

## 📚 KEY FEATURES

### ✅ Đã refactor sang Clean Architecture:

- QL Sinh viên PDT (CRUD + Import)
- Payment (VNPay + MoMo)
- Tuition (Tính học phí)
- Báo cáo thống kê
- Quản lý học kỳ & Phase
- Danh mục (Khoa, Ngành, Cơ sở)

### ⚠️ Chưa refactor (vẫn dùng modules/):

- SV: Đăng ký học phần
- SV: Ghi danh
- SV: TKB
- GV: Quản lý lớp
- TK/TLK: Đề xuất học phần

---

## 🎯 CONVENTION & BEST PRACTICES

1. **Naming:**

   - Use cases: `<Verb><Noun>UseCase` (e.g., `UpdateSinhVienUseCase`)
   - Controllers: `<Noun>Controller`
   - Repositories: `<Noun>Repository`
   - DTOs: `<Action><Noun>DTO`

2. **Error Handling:**

   - Use `ServiceResult<T>` pattern
   - Define error codes (e.g., `SINH_VIEN_NOT_FOUND`)
   - Throw domain exceptions in entities

3. **Transaction:**

   - Always use UnitOfWork for multi-table operations
   - Prisma transactions: `prisma.$transaction()`

4. **Authentication:**
   - Middleware: `requireAuth`, `requireRole([roles])`
   - JWT token in `Authorization: Bearer <token>`
   - Decoded to `req.auth = { userId, role, ... }`

---

## 📊 API RESPONSE FORMAT

```typescript
// Success
{
  "isSuccess": true,
  "message": "Success message",
  "data": { ... }
}

// Error
{
  "isSuccess": false,
  "message": "Error message",
  "errorCode": "ERROR_CODE"
}

// Paginated
{
  "isSuccess": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```

---

## 🔐 SECURITY

- Password hashing: bcrypt
- JWT authentication
- Role-based access control (RBAC)
- CORS enabled
- Helmet.js for security headers
- Request validation (DTOs)

---

## 📦 DEPENDENCIES

**Core:**

- express
- prisma
- inversify (DI)
- bcrypt
- jsonwebtoken
- cors, helmet

**Payment:**

- crypto (VNPay signature)
- axios (MoMo API)

**Utils:**

- date-fns
- xlsx (Excel import/export)

---

## 🚀 MIGRATION STRATEGY TO DJANGO

### Recommend approach:

1. **Database**: Giữ nguyên schema PostgreSQL, dùng Django inspectdb
2. **Authentication**: Django REST Framework + JWT
3. **Architecture**: Dùng Django app structure tương tự modules
4. **Patterns**:
   - Use Django Class-Based Views (CBV) → Controllers
   - Service Layer → Use Cases
   - Repository → Django ORM Managers
   - DTOs → Serializers (DRF)

---

## 📝 NOTES

- Project đang trong quá trình refactor từ feature-based (`modules/`) sang Clean Architecture (`application/`, `interface/`)
- Một số endpoints có 2 implementation (legacy vs clean)
- MongoDB chỉ dùng cho tài liệu (documents), còn lại dùng PostgreSQL
- Phase system rất quan trọng: kiểm soát thời gian ghi danh, đăng ký, hủy đăng ký
