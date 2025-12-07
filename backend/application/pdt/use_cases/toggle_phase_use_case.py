from datetime import datetime, timedelta
from django.utils import timezone
from core.types import ServiceResult
from infrastructure.persistence.models import KyPhase

class TogglePhaseUseCase:
    def execute(self, hoc_ky_id: str | None, phase_name: str) -> ServiceResult:
        try:
            # If hoc_ky_id is missing, get current
            if not hoc_ky_id:
                from infrastructure.persistence.enrollment.repositories import HocKyRepository
                current_hk = HocKyRepository().get_current_hoc_ky()
                if not current_hk:
                    return ServiceResult.fail("Không tìm thấy học kỳ hiện hành")
                hoc_ky_id = str(current_hk.id)

            # Validate phase name
            # Values must match legacy system (be-egacy) and DB constraints
            valid_phases = [
                'de_xuat_phe_duyet', 
                'ghi_danh', 
                'dang_ky_hoc_phan', 
                'sap_xep_tkb', 
                'binh_thuong'
            ]
            
            if phase_name not in valid_phases:
                return ServiceResult.fail(f"Phase không hợp lệ. Valid: {', '.join(valid_phases)}")

            # 1. Disable all phases for this semester
            KyPhase.objects.using('neon').filter(hoc_ky_id=hoc_ky_id).update(
                is_enabled=False,
                start_at=timezone.now() - timedelta(days=365), # Move to past
                end_at=timezone.now() - timedelta(days=364)
            )

            # 2. Enable the selected phase
            # Check if exists
            phase = KyPhase.objects.using('neon').filter(hoc_ky_id=hoc_ky_id, phase=phase_name).first()
            
            now = timezone.now()
            start_at = now - timedelta(hours=1)
            end_at = now + timedelta(days=30)
            
            if phase:
                phase.is_enabled = True
                phase.start_at = start_at
                phase.end_at = end_at
                phase.save(using='neon')
            else:
                return ServiceResult.fail(f"Không tìm thấy phase '{phase_name}' trong học kỳ này (dữ liệu chưa được khởi tạo)")
                
            return ServiceResult.ok({
                "message": f"Đã chuyển sang giai đoạn: {phase_name}",
                "active_phase": phase_name,
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat()
            })
            
        except Exception as e:
            return ServiceResult.fail(str(e))
