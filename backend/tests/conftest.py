import pytest
import os
from pathlib import Path
from django.conf import settings

# Load .env.test file if it exists (for test database credentials)
def load_env_test():
    """Load environment variables from .env.test file"""
    env_test_path = Path(__file__).parent.parent / '.env.test'
    if env_test_path.exists():
        print(f"\nDEBUG: Loading .env.test from {env_test_path}")
        with open(env_test_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    else:
        print(f"\nDEBUG: .env.test not found at {env_test_path}")

# Load env vars at module import time
load_env_test()


@pytest.fixture(scope='session')
def django_db_setup(django_test_environment, django_db_blocker):
    """
    Configure database for tests.
    By default, use the TEST config from settings.py (which points to real DB).
    Only switch to SQLite if USE_SQLITE_FOR_TESTS is set to 'true'.
    """
    use_sqlite = os.getenv('USE_SQLITE_FOR_TESTS', 'false').lower() == 'true'
    
    with django_db_blocker.unblock():
        # Ensure TEST key exists for neon database
        if 'TEST' not in settings.DATABASES.get('neon', {}):
            print("\nDEBUG: TEST key missing in neon config, adding default TEST config")
            if 'neon' not in settings.DATABASES:
                settings.DATABASES['neon'] = {}
            settings.DATABASES['neon']['TEST'] = {
                'NAME': os.getenv('TEST_DB_NAME', 'test_neondb'),
                'USER': os.getenv('TEST_DB_USER', 'neondb_owner'),
                'PASSWORD': os.getenv('TEST_DB_PASSWORD', ''),
                'HOST': os.getenv('TEST_DB_HOST', ''),
                'PORT': os.getenv('TEST_DB_PORT', '5432'),
                'OPTIONS': {
                    'sslmode': os.getenv('TEST_DB_SSLMODE', 'require'),
                },
                'DEPENDENCIES': [],
            }
        
        if use_sqlite:
            print("\nDEBUG: Switching to SQLite for tests (USE_SQLITE_FOR_TESTS=true)")
            settings.DATABASES['default']['TEST'] = {
                'NAME': ':memory:',
            }
            settings.DATABASES['neon'] = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                'TEST': {
                    'NAME': ':memory:',
                },
            }
        else:
            print("\nDEBUG: Using configured TEST databases (Real DB)")
            print(f"DEBUG: neon TEST config: {settings.DATABASES.get('neon', {}).get('TEST', 'STILL MISSING')}")


def pytest_runtest_setup(item):
    """Debug hook to check database config before each test"""
    pass  # Remove noisy debug output


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def create_test_account():
    def _create_account(username, password, loai='sinh_vien', active=True):
        from infrastructure.persistence.models import Users, TaiKhoan
        import uuid
        from core.utils.password import PasswordService
        
        tai_khoan = TaiKhoan.objects.create(
            id=uuid.uuid4(),
            ten_dang_nhap=username,
            mat_khau=PasswordService.hash_password(password),
            loai_tai_khoan=loai,
            trang_thai_hoat_dong=active
        )
        
        user = Users.objects.create(
            id=uuid.uuid4(),
            ho_ten=f"Test User {username}",
            email=f"{username}@example.com",
            tai_khoan=tai_khoan
        )
        return tai_khoan
    return _create_account

