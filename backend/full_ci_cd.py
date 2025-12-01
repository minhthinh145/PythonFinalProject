#!/usr/bin/env python3
"""
FULL CI/CD TEST SUITE
=====================
Chạy toàn bộ test suite cho backend

Usage:
    python full_ci_cd.py                    # Chạy tất cả tests
    python full_ci_cd.py --unit             # Chỉ unit tests
    python full_ci_cd.py --integration      # Chỉ integration tests  
    python full_ci_cd.py --e2e              # Chỉ e2e tests
    python full_ci_cd.py --fast             # SQLite in-memory (nhanh)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}  {text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def print_info(text: str):
    print(f"{Colors.CYAN}ℹ {text}{Colors.NC}")

def run_command(cmd: list, env: dict = None) -> tuple:
    """Run a command and return (success, output)"""
    try:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=merged_env,
            cwd=Path(__file__).parent
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_environment():
    """Check Python and Django are properly configured"""
    print_header("Step 1: Checking Environment")
    
    # Check Python version
    success, output = run_command([sys.executable, "--version"])
    if success:
        print_success(f"Python: {output.strip()}")
    else:
        print_error("Python check failed")
        return False
    
    # Check Django
    success, output = run_command([
        sys.executable, "-c", 
        "import django; print(f'Django {django.__version__}')"
    ])
    if success:
        print_success(output.strip())
    else:
        print_error("Django not installed")
        return False
    
    # Check pytest
    success, output = run_command([
        sys.executable, "-c",
        "import pytest; print(f'Pytest {pytest.__version__}')"
    ])
    if success:
        print_success(output.strip())
    else:
        print_warning("Pytest not installed, installing...")
        run_command([sys.executable, "-m", "pip", "install", "pytest", "pytest-django"])
    
    return True

def check_database():
    """Check database connection"""
    print_header("Step 2: Checking Database Connection")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
    
    success, output = run_command([
        sys.executable, "manage.py", "check", "--database", "neon"
    ])
    
    if success:
        print_success("Database connection OK")
        return True
    else:
        print_error(f"Database connection failed:\n{output}")
        return False

def run_tests(test_path: str, name: str, env: dict = None) -> bool:
    """Run pytest for a specific test path"""
    print_header(f"Running {name}")
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "-q",
        "--no-header"
    ]
    
    success, output = run_command(cmd, env)
    
    # Print output
    print(output)
    
    if success:
        print_success(f"{name} PASSED")
    else:
        print_error(f"{name} FAILED")
    
    return success

def run_unit_tests(use_sqlite: bool = False) -> bool:
    """Run unit tests"""
    env = {"USE_SQLITE_FOR_TESTS": "true"} if use_sqlite else None
    return run_tests("tests/unit/", "Unit Tests", env)

def run_integration_tests(use_sqlite: bool = False) -> bool:
    """Run integration tests"""
    env = {"USE_SQLITE_FOR_TESTS": "true"} if use_sqlite else None
    return run_tests("tests/integration/", "Integration Tests", env)

def run_e2e_tests(use_sqlite: bool = False) -> bool:
    """Run E2E tests"""
    env = {"USE_SQLITE_FOR_TESTS": "true"} if use_sqlite else None
    return run_tests("tests/e2e/", "E2E Tests", env)

def print_summary(results: dict):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.NC}" if passed else f"{Colors.RED}FAILED{Colors.NC}"
        icon = "✓" if passed else "✗"
        print(f"  {icon} {name}: {status}")
    
    print()
    if all_passed:
        print(f"{Colors.GREEN}{'='*50}")
        print(f"  ALL TESTS PASSED! 🎉")
        print(f"{'='*50}{Colors.NC}")
        return 0
    else:
        print(f"{Colors.RED}{'='*50}")
        print(f"  SOME TESTS FAILED!")
        print(f"{'='*50}{Colors.NC}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Full CI/CD Test Suite")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run only E2E tests")
    parser.add_argument("--fast", action="store_true", help="Use SQLite in-memory (faster)")
    parser.add_argument("--skip-env-check", action="store_true", help="Skip environment check")
    parser.add_argument("--skip-db-check", action="store_true", help="Skip database check")
    
    args = parser.parse_args()
    
    # Determine which tests to run
    run_all = not (args.unit or args.integration or args.e2e)
    use_sqlite = args.fast
    
    print(f"\n{Colors.CYAN}{'='*50}")
    print(f"  FULL CI/CD TEST SUITE")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}{Colors.NC}")
    
    if use_sqlite:
        print_warning("Using SQLite in-memory mode (--fast)")
    
    results = {}
    
    # Step 1: Environment check
    if not args.skip_env_check:
        if not check_environment():
            print_error("Environment check failed!")
            return 1
        results["Environment"] = True
    
    # Step 2: Database check
    if not args.skip_db_check and not use_sqlite:
        if not check_database():
            print_warning("Database check failed, continuing anyway...")
            results["Database"] = False
        else:
            results["Database"] = True
    
    # Step 3: Run tests
    if run_all or args.unit:
        results["Unit Tests"] = run_unit_tests(use_sqlite)
    
    if run_all or args.integration:
        results["Integration Tests"] = run_integration_tests(use_sqlite)
    
    if run_all or args.e2e:
        results["E2E Tests"] = run_e2e_tests(use_sqlite)
    
    # Summary
    return print_summary(results)

if __name__ == "__main__":
    sys.exit(main())
