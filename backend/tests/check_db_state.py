from infrastructure.persistence.models import HocKy, KyPhase

def check_state():
    print("--- Checking Database State ---")
    
    # 1. Check Current Semester
    hk = HocKy.objects.using('neon').filter(trang_thai_hien_tai=True).first()
    if not hk:
        print("❌ No current semester (trang_thai_hien_tai=True)")
        return
    
    print(f"✅ Current Semester: {hk.ten_hoc_ky} (ID: {hk.id})")
    
    # 2. Check Phases for this Semester
    phases = KyPhase.objects.using('neon').filter(hoc_ky_id=hk.id)
    print(f"ℹ️  Found {phases.count()} phases for this semester:")
    
    active_phase = None
    for p in phases:
        status = "✅ ACTIVE" if p.is_enabled else "❌ INACTIVE"
        print(f"   - Phase: {p.phase}, Start: {p.start_at}, End: {p.end_at}, Enabled: {p.is_enabled} [{status}]")
        if p.is_enabled:
            active_phase = p
            
    if not active_phase:
        print("❌ No active phase found")
    elif active_phase.phase != "ghi_danh":
        print(f"❌ Active phase is '{active_phase.phase}', expected 'ghi_danh'")
    else:
        print("✅ Active phase is 'ghi_danh'")

if __name__ == "__main__":
    check_state()
