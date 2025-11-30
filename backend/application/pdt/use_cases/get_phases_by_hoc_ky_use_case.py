from typing import List, Dict, Any
from application.enrollment.interfaces.repositories import IKyPhaseRepository
from core.types.service_result import ServiceResult

class GetPhasesByHocKyUseCase:
    def __init__(self, ky_phase_repo: IKyPhaseRepository):
        self.ky_phase_repo = ky_phase_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult[Dict[str, Any]]:
        try:
            phases = self.ky_phase_repo.find_by_hoc_ky(hoc_ky_id)
            
            data = []
            for p in phases:
                data.append({
                    "id": str(p.id),
                    "phase": p.phase,
                    "startAt": p.start_at,
                    "endAt": p.end_at,
                    "isEnabled": p.is_enabled
                })
                
            return ServiceResult.ok({"phases": data})
        except Exception as e:
            return ServiceResult.fail(str(e))
