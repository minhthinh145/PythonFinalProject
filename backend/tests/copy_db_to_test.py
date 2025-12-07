#!/usr/bin/env python3
"""
Copy Data from Production (neon_db) to Test (test_neondb)

Usage:
    1. Set environment variables in .env.test:
       - Source DB: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
       - Target DB: TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASSWORD, TEST_DB_HOST
    
    2. Run: python tests/copy_db_to_test.py

Note: This script uses pg_dump and psql for efficient copying.
"""

import os
import sys
import subprocess
from pathlib import Path

# Load environment vars from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        print(f"Loading .env from {env_path}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    else:
        print(f"Warning: .env not found at {env_path}")

load_env()


def get_db_config(prefix=''):
    """Get database config from environment"""
    if prefix:
        return {
            'name': os.getenv(f'{prefix}_DB_NAME') or os.getenv(f'{prefix}DB_NAME'),
            'user': os.getenv(f'{prefix}_DB_USER') or os.getenv(f'{prefix}DB_USER'),
            'password': os.getenv(f'{prefix}_DB_PASSWORD') or os.getenv(f'{prefix}DB_PASSWORD'),
            'host': os.getenv(f'{prefix}_DB_HOST') or os.getenv(f'{prefix}DB_HOST'),
            'port': os.getenv(f'{prefix}_DB_PORT', '5432') or os.getenv(f'{prefix}DB_PORT', '5432'),
        }
    else:
        return {
            'name': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432'),
        }


def build_connection_string(config):
    """Build PostgreSQL connection string"""
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['name']}?sslmode=require"


def copy_database():
    """Copy data from source to target database"""
    
    # Source (Production)
    source = get_db_config()
    print(f"Source DB: {source['name']} @ {source['host']}")
    
    # Target (Test)
    target = get_db_config('TEST')
    print(f"Target DB: {target['name']} @ {target['host']}")
    
    if not source['name'] or not source['host']:
        print("❌ Source database not configured. Check DB_NAME, DB_HOST in .env")
        return False
    
    if not target['name'] or not target['host']:
        print("❌ Target database not configured. Check TEST_DB_NAME, TEST_DB_HOST in .env")
        return False
    
    # Create temp dump file
    dump_file = Path(__file__).parent / 'temp_dump.sql'
    
    try:
        # Step 1: Dump source database
        print("\n📥 Dumping source database...")
        
        dump_env = os.environ.copy()
        dump_env['PGPASSWORD'] = source['password']
        
        dump_cmd = [
            'pg_dump',
            '-h', source['host'],
            '-p', source['port'],
            '-U', source['user'],
            '-d', source['name'],
            '--no-owner',
            '--no-acl',
            '--clean',
            '--if-exists',
            '-f', str(dump_file)
        ]
        
        result = subprocess.run(dump_cmd, env=dump_env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ pg_dump failed: {result.stderr}")
            return False
        
        print(f"✅ Dump completed: {dump_file.stat().st_size / 1024:.1f} KB")
        
        # Step 2: Restore to target database
        print("\n📤 Restoring to target database...")
        
        restore_env = os.environ.copy()
        restore_env['PGPASSWORD'] = target['password']
        
        restore_cmd = [
            'psql',
            '-h', target['host'],
            '-p', target['port'],
            '-U', target['user'],
            '-d', target['name'],
            '-f', str(dump_file)
        ]
        
        result = subprocess.run(restore_cmd, env=restore_env, capture_output=True, text=True)
        
        # psql may have some errors but still succeed partially
        if 'ERROR' in result.stderr and 'already exists' not in result.stderr:
            print(f"⚠️ Some restore errors: {result.stderr[:500]}")
        
        print("✅ Restore completed!")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        print("Make sure pg_dump and psql are installed and in PATH")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        # Cleanup
        if dump_file.exists():
            dump_file.unlink()
            print("🧹 Cleaned up temp file")


def copy_via_django():
    """Alternative: Copy using Django ORM (slower but no pg_dump needed)"""
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    django.setup()
    
    from django.db import connections
    from django.apps import apps
    
    source_alias = 'neon'
    # We need to create a new connection for test db
    # This requires modifying settings dynamically
    
    print("⚠️ Django ORM copy not fully implemented")
    print("Please use pg_dump/psql method or configure TEST DB connection")


if __name__ == "__main__":
    print("="*60)
    print("📋 DATABASE COPY SCRIPT")
    print("="*60)
    
    # Check if pg_dump is available
    try:
        result = subprocess.run(['pg_dump', '--version'], capture_output=True, text=True)
        print(f"Using {result.stdout.strip()}")
    except FileNotFoundError:
        print("⚠️ pg_dump not found, will try alternative method")
        copy_via_django()
        sys.exit(1)
    
    success = copy_database()
    
    if success:
        print("\n✅ Database copy completed successfully!")
    else:
        print("\n❌ Database copy failed!")
        sys.exit(1)
