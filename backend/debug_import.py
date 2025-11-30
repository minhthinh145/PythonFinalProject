import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DKHPHCMUE.settings')
django.setup()

try:
    from presentation.api.course_registration.views import GetChiTietHocPhiView
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
