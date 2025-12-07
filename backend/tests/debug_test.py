import pytest
from django.conf import settings
from django.db import connections

@pytest.mark.django_db
def test_print_db_settings():
    import sys
    import DKHPHCMUE.settings as app_settings
    
    print(f"\nDEBUG: sys.path: {sys.path}")
    print(f"DEBUG: app_settings file: {app_settings.__file__}")
    
    print("\nDEBUG: Inspecting app_settings.DATABASES (DIRECT IMPORT)...")
    if 'neon' in app_settings.DATABASES:
        print(f"  neon keys: {list(app_settings.DATABASES['neon'].keys())}")
        if 'TEST' in app_settings.DATABASES['neon']:
            print(f"  neon TEST: {app_settings.DATABASES['neon']['TEST']}")
        else:
            print("  neon TEST: MISSING")
            
    print("\nDEBUG: Inspecting django.conf.settings.DATABASES (RUNTIME)...")
    for alias, db_settings in settings.DATABASES.items():
        print(f"DB '{alias}': keys={list(db_settings.keys())}")
        if 'TEST' in db_settings:
            print(f"  TEST config: {db_settings['TEST']}")
        else:
            print(f"  TEST config: MISSING")

    print("\nDEBUG: Inspecting connections...")
    for alias in connections:
        conn = connections[alias]
        print(f"Connection '{alias}': settings_dict keys={list(conn.settings_dict.keys())}")
        if 'TEST' in conn.settings_dict:
            print(f"  TEST config: {conn.settings_dict['TEST']}")
        else:
            print(f"  TEST config: MISSING")
            
    assert True
