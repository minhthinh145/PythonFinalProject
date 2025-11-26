# Hệ thống Đăng ký Học phần - HCMUE

> Một hệ thống đăng ký học phần hiện đại được xây dựng với Django REST Framework cho Backend và React (Vite) cho Frontend. Database sử dụng PostgreSQL trên Neon.

---

## 📖 Mục lục

- [🛠️ Công nghệ sử dụng](#️-công-nghệ-sử-dụng)
- [📂 Cấu trúc dự án](#-cấu-trúc-dự-án)
- [📋 Yêu cầu tiên quyết](#-yêu-cầu-tiên-quyết)
- [📥 Tải về và Cài đặt](#-tải-về-và-cài-đặt)
  - [Phương án 1: Cài đặt với Docker (Khuyến nghị)](#phương-án-1-cài-đặt-với-docker-khuyến-nghị)
  - [Phương án 2: Cài đặt Development](#phương-án-2-cài-đặt-development)
- [💡 Các lệnh hữu ích](#-các-lệnh-hữu-ích)
- [� Bảo mật](#-bảo-mật)

---

## 🛠️ Công nghệ sử dụng

| Lĩnh vực             | Công nghệ                                                                                                                                                                                           |
| :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend**         | [React](https://reactjs.org/), [Vite](https://vitejs.dev/), [Redux Toolkit](https://redux-toolkit.js.org/), [React Router](https://reactrouter.com/), [TypeScript](https://www.typescriptlang.org/) |
| **Backend**          | [Django 5.2](https://www.djangoproject.com/), [Django REST Framework](https://www.django-rest-framework.org/), [Python 3.11](https://www.python.org/)                                               |
| **Cơ sở dữ liệu**    | [PostgreSQL on Neon](https://neon.tech/)                                                                                                                                                            |
| **Containerization** | [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/)                                                                                                               |

---

## 📂 Cấu trúc dự án

Dự án được tổ chức với Frontend và Backend tách biệt:

```
PythonProject/
├── backend/
│   ├── DKHPHCMUE/          # Django project settings
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/                # Source code Frontend (React + Vite)
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment variables template
├── .gitignore
└── README.md
```

└── README.md

````

---

## 📋 Yêu cầu tiên quyết

### Cho Người dùng cuối (Phương án Docker):

- **Docker Desktop** ([Tải về Docker Desktop](https://www.docker.com/products/docker-desktop))
- **Neon PostgreSQL Account** ([Đăng ký miễn phí tại Neon.tech](https://neon.tech/))

### Cho Developer (Phương án Development):

- **Python**: `v3.11` trở lên
- **Node.js**: `v18.x` trở lên
- **PNPM**: `v8.x` trở lên ([Hướng dẫn cài đặt PNPM](https://pnpm.io/installation))
- **Git**
- **Neon PostgreSQL Account**

---

## 📥 Tải về và Cài đặt

### Phương án 1: Cài đặt với Docker (Khuyến nghị)

> ⚡ **Phương án này cho phép chạy toàn bộ hệ thống chỉ với Docker**

#### � Hướng dẫn Cài đặt

**Bước 1: Clone repository**

```bash
git clone https://github.com/DuongThanhTaii/DangKyHocPhanHCMUE-CNPM.git
cd DangKyHocPhanHCMUE-CNPM
````

**Bước 2: Tạo database trên Neon**

1. Truy cập [Neon Console](https://console.neon.tech)
2. Tạo project mới
3. Copy connection string (format: `postgresql://user:password@host/database?sslmode=require`)

**Bước 3: Cấu hình môi trường**

```bash
# Copy file .env.example thành .env
cp .env.example .env

# Chỉnh sửa file .env và điền thông tin:
# - DATABASE_URL: Connection string từ Neon
# - SECRET_KEY: Tạo secret key mới cho Django
```

**Bước 4: Khởi động ứng dụng**

```bash
# Build và start cả Frontend + Backend
docker-compose up --build -d
```

> ⏳ **Lưu ý:** Lần đầu chạy có thể mất 5-10 phút để build Docker images.

**Bước 5: Kiểm tra trạng thái**

```bash
docker-compose ps
```

Đảm bảo tất cả các service đều có trạng thái **Up**.

**Bước 6: Truy cập ứng dụng**

Sau khi các container khởi động thành công:

- **Frontend (Giao diện người dùng):** [http://localhost](http://localhost)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Django Admin:** [http://localhost:8000/admin](http://localhost:8000/admin)

---

#### 🛑 Dừng và Gỡ bỏ

**Dừng ứng dụng:**

```bash
docker-compose down
```

**Khởi động lại:**

```bash
docker-compose up -d
```

**Xem logs:**

```bash
# Xem tất cả logs
docker-compose logs -f

# Xem logs của service cụ thể
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

#### ❓ Xử lý Sự cố

**Lỗi: Port đã được sử dụng**

Nếu gặp lỗi `port already allocated`, có nghĩa là port đang được sử dụng bởi ứng dụng khác. Sửa file `docker-compose.yaml`:

```yaml
# Đổi port database
ports:
  - "5434:5432"  # Thay vì 5433:5432

# Đổi port backend
ports:
  - "3001:3000"  # Thay vì 3000:3000

# Đổi port frontend
ports:
  - "5174:5173"  # Thay vì 5173:5173
```

**Lỗi: Không kết nối được database**

```bash
# Kiểm tra logs của database
docker-compose logs db

# Khởi động lại database
docker-compose restart db

# Nếu vẫn lỗi, xóa và tạo lại
docker-compose down -v
docker-compose up -d
```

**Lỗi: Docker Desktop chưa khởi động**

Đảm bảo Docker Desktop đang chạy trước khi thực hiện các lệnh `docker-compose`.

---

### Phương án 2: Cài đặt Development

> 👨‍💻 **Phương án này dành cho developer muốn phát triển và chỉnh sửa code**

#### Bước 1: Clone Repository

```bash
git clone https://github.com/DuongThanhTaii/DangKyHocPhanHCMUE-CNPM.git
cd DangKyHocPhanHCMUE-CNPM
```

#### Bước 2: Cấu hình Database trên Neon

1. Truy cập [Neon Console](https://console.neon.tech)
2. Tạo project mới và database
3. Copy connection string

#### Bước 3: Cấu hình Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc venv\Scripts\activate trên Windows

# Install dependencies
pip install -r requirements.txt

# Tạo file .env
cp ../.env.example .env
# Chỉnh sửa .env và điền DATABASE_URL từ Neon

# Migrate database
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Backend sẽ chạy tại: [http://localhost:8000](http://localhost:8000)

#### Bước 4: Cấu hình Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Run dev server
pnpm run dev
```

Frontend sẽ chạy tại: [http://localhost:5173](http://localhost:5173)

#### Bước 5: Chạy Backend và Frontend

Sử dụng lệnh `dev` ở thư mục gốc để khởi động đồng thời cả hai ứng dụng.

```bash
pnpm dev
```

#### Bước 6: Truy cập ứng dụng

Sau khi các tiến trình khởi động thành công:

- **Frontend (Giao diện người dùng):** [http://localhost:5173](http://localhost:5173) (Port mặc định của Vite)
- **Backend (API Server):** [http://localhost:3000](http://localhost:3000)
- **Kết nối Database:** Host: `localhost`, Port: `5433`

---

## 💡 Các lệnh hữu ích

### Lệnh Docker (Cho người dùng)

```bash
# Kiểm tra trạng thái các container
docker-compose ps

# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của một service cụ thể
docker-compose logs -f backend
docker-compose logs -f frontend

# Khởi động lại tất cả services
docker-compose restart

# Khởi động lại một service cụ thể
docker-compose restart backend

# Dừng ứng dụng
docker-compose down

# Rebuild và restart
docker-compose up --build -d

# Cập nhật images mới nhất
docker-compose pull
docker-compose up -d
```

---

### Lệnh Django trong Docker

```bash
# Chạy migration
docker-compose exec backend python manage.py migrate

# Tạo superuser
docker-compose exec backend python manage.py createsuperuser

# Tạo migration mới
docker-compose exec backend python manage.py makemigrations

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Mở Django shell
docker-compose exec backend python manage.py shell
```

---

### Lệnh Development (không dùng Docker)

**Backend:**

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver

# Create new migration
python manage.py makemigrations

# Open Django shell
python manage.py shell
```

**Frontend:**

```bash
cd frontend

# Install dependencies
pnpm install

# Run dev server
pnpm run dev

# Build for production
pnpm run build

# Preview production build
pnpm run preview

# Lint code
pnpm run lint
```

---

## 🔒 Bảo mật

- ⚠️ **Không** commit file `.env` lên Git
- 🔑 Thay đổi `SECRET_KEY` trong production
- 🚫 Set `DEBUG=False` trong production
- 🌐 Cấu hình `ALLOWED_HOSTS` phù hợp với domain
- 🔐 Sử dụng SSL/HTTPS trong production
- 🛡️ Cập nhật dependencies định kỳ để vá lỗi bảo mật

---

## 📄 Giấy phép

Dự án này được cấp phép theo Giấy phép MIT.

---
