# Hướng dẫn Khởi động nhanh

## 🚀 Chạy bằng Docker (Khuyến nghị)

### Bước 1: Chuẩn bị Database

1. Tạo tài khoản miễn phí tại [Neon.tech](https://neon.tech)
2. Tạo database mới
3. Copy connection string (dạng: `postgresql://user:password@host/database?sslmode=require`)

### Bước 2: Cấu hình môi trường

```bash
# Copy file .env.example thành .env
cp .env.example .env

# Mở file .env và điền thông tin:
# DATABASE_URL=<connection-string-từ-neon>
# SECRET_KEY=<tạo-key-mới-bất-kỳ>
```

### Bước 3: Khởi động

```bash
# Build và start
docker-compose up --build -d

# Kiểm tra trạng thái
docker-compose ps

# Tạo superuser cho Django admin
docker-compose exec backend python manage.py createsuperuser
```

### Bước 4: Truy cập

- Frontend: http://localhost
- Backend API: http://localhost:8000
- Django Admin: http://localhost:8000/admin

---

## 🛠️ Chạy Development (không Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # hoặc venv\Scripts\activate trên Windows
pip install -r requirements.txt

# Tạo file .env và điền thông tin
cp ../.env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
pnpm install
pnpm run dev
```

---

## 📝 Lệnh thường dùng

### Docker

```bash
# Xem logs
docker-compose logs -f

# Restart
docker-compose restart

# Dừng
docker-compose down

# Chạy lệnh Django
docker-compose exec backend python manage.py <command>
```

### Development

```bash
# Backend
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
pnpm run dev
```

---

## ❓ Troubleshooting

**Port đã được sử dụng?**

- Chỉnh sửa ports trong `docker-compose.yml`

**Không kết nối được database?**

- Kiểm tra `DATABASE_URL` trong file `.env`
- Kiểm tra connection string từ Neon có đúng không

**Frontend không gọi được API?**

- Kiểm tra `CORS_ALLOWED_ORIGINS` trong `.env`
- Kiểm tra Backend đã chạy chưa
