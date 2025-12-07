import pytest
from unittest.mock import MagicMock, patch
from application.pdt.use_cases.toggle_phase_use_case import TogglePhaseUseCase
from infrastructure.persistence.models import KyPhase, HocKy
from django.utils import timezone
from datetime import timedelta
import uuid

@pytest.mark.django_db(databases=['neon'])
class TestTogglePhaseUseCase:
    def test_execute_toggles_phase_correctly(self):
        # Setup
        hoc_ky_id = uuid.uuid4()
        
        # Mock HocKyRepository if needed, but we can just pass hoc_ky_id
        
        # Seed phases
        phases = ['de_xuat_phe_duyet', 'ghi_danh', 'dang_ky_hoc_phan']
        for p in phases:
            KyPhase.objects.using('neon').create(
                id=uuid.uuid4(),
                hoc_ky_id=hoc_ky_id,
                phase=p,
                start_at=timezone.now(),
                end_at=timezone.now() + timedelta(days=30),
                is_enabled=(p == 'de_xuat_phe_duyet') # Initially de_xuat is enabled
            )
            
        use_case = TogglePhaseUseCase()
        
        # Execute: Toggle 'ghi_danh'
        result = use_case.execute(str(hoc_ky_id), 'ghi_danh')
        
        # Verify
        assert result.success
        
        # Check 'ghi_danh' is enabled
        ghi_danh = KyPhase.objects.using('neon').get(hoc_ky_id=hoc_ky_id, phase='ghi_danh')
        assert ghi_danh.is_enabled == True
        
        # Check 'de_xuat_phe_duyet' is disabled
        de_xuat = KyPhase.objects.using('neon').get(hoc_ky_id=hoc_ky_id, phase='de_xuat_phe_duyet')
        assert de_xuat.is_enabled == False
        
        # Check total count (should be 3, no new rows)
        count = KyPhase.objects.using('neon').filter(hoc_ky_id=hoc_ky_id).count()
        assert count == 3

    def test_execute_fails_if_phase_not_found(self):
        hoc_ky_id = uuid.uuid4()
        use_case = TogglePhaseUseCase()
        
        # Execute with non-existent phase (but valid enum)
        # Note: 'ghi_danh' is valid enum but not seeded in this test case
        result = use_case.execute(str(hoc_ky_id), 'ghi_danh')
        
        # Verify
        assert not result.success
        assert "Không tìm thấy phase" in result.message or "Phase không hợp lệ" in result.message
