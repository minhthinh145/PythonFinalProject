from typing import List, Dict, Any
from datetime import datetime
import uuid
from core.types import ServiceResult
from application.pdt.interfaces.repositories import IKyPhaseRepository, IHocKyRepository
from application.enrollment.interfaces.repositories import IDotDangKyRepository


def parse_datetime(dt_str: str) -> datetime:
    """
    Parse datetime string with multiple format support.
    Handles: ISO format with timezone, datetime string, date-only string.
    """
    if not dt_str:
        raise ValueError("Empty datetime string")
    
    # Remove trailing 'Z' if present (UTC marker)
    dt_str = dt_str.replace('Z', '').replace('z', '')
    
    # Try multiple formats
    formats = [
        '%Y-%m-%dT%H:%M:%S.%f',  # ISO with milliseconds
        '%Y-%m-%dT%H:%M:%S',      # ISO without milliseconds
        '%Y-%m-%d %H:%M:%S',      # Standard datetime
        '%Y-%m-%d',               # Date only
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Cannot parse datetime: {dt_str}")


class CreateBulkKyPhaseUseCase:
    def __init__(self, 
                 ky_phase_repo: IKyPhaseRepository,
                 hoc_ky_repo: IHocKyRepository,
                 dot_dang_ky_repo: IDotDangKyRepository):
        self.ky_phase_repo = ky_phase_repo
        self.hoc_ky_repo = hoc_ky_repo
        self.dot_dang_ky_repo = dot_dang_ky_repo

    def execute(self, data: Dict[str, Any]) -> ServiceResult:
        hoc_ky_id = data.get('hocKyId')
        hoc_ky_start_at_str = data.get('hocKyStartAt')
        hoc_ky_end_at_str = data.get('hocKyEndAt')
        phases = data.get('phases')

        # 1. Validate Input
        if not hoc_ky_id or not hoc_ky_start_at_str or not hoc_ky_end_at_str:
             return ServiceResult.fail("Thiếu thông tin học kỳ", error_code="MISSING_PARAMS")
        
        if not phases or not isinstance(phases, list) or len(phases) == 0:
             return ServiceResult.fail("Danh sách phases rỗng", error_code="MISSING_PARAMS")

        try:
            hoc_ky_start_at = parse_datetime(hoc_ky_start_at_str)
            hoc_ky_end_at = parse_datetime(hoc_ky_end_at_str)
        except ValueError as e:
             return ServiceResult.fail(f"Định dạng ngày không hợp lệ: {e}", error_code="INVALID_DATE_FORMAT")

        if hoc_ky_start_at >= hoc_ky_end_at:
            return ServiceResult.fail("Thời gian bắt đầu học kỳ phải trước thời gian kết thúc", error_code="INVALID_TIME_RANGE")

        # 2. Update Hoc Ky Dates
        self.hoc_ky_repo.update_dates(hoc_ky_id, hoc_ky_start_at, hoc_ky_end_at)

        # 3. Cleanup Old Data
        # Note: ky_phase_repo.create_bulk already deletes old phases for the semester
        self.dot_dang_ky_repo.delete_by_hoc_ky(hoc_ky_id)

        # 4. Create New Phases
        # Note: ky_phase_repo.create_bulk handles creation and returns DTOs
        # We need to ensure phases have correct date format for the repo if it expects strings or datetimes
        # The repo implementation currently parses 'ngayBatDau'/'ngayKetThuc' from dict
        # But FE sends 'startAt'/'endAt'. We need to map it.
        mapped_phases = []
        for p in phases:
            mapped_phases.append({
                "tenPhase": p.get('phase'),
                "ngayBatDau": p.get('startAt'), # Repo expects YYYY-MM-DD string
                "ngayKetThuc": p.get('endAt')
            })

        created_phases = self.ky_phase_repo.create_bulk(mapped_phases, hoc_ky_id)

        # 5. Create Default Dot Dang Ky
        ghi_danh_phase = next((p for p in phases if p.get('phase') == 'ghi_danh'), None)
        dang_ky_phase = next((p for p in phases if p.get('phase') == 'dang_ky_hoc_phan'), None)

        if ghi_danh_phase:
            self.dot_dang_ky_repo.create({
                "hoc_ky_id": hoc_ky_id,
                "loai_dot": "ghi_danh",
                "is_check_toan_truong": True,
                "thoi_gian_bat_dau": parse_datetime(ghi_danh_phase.get('startAt')),
                "thoi_gian_ket_thuc": parse_datetime(ghi_danh_phase.get('endAt')),
                "gioi_han_tin_chi": 50,
                "khoa_id": None
            })

        if dang_ky_phase:
             self.dot_dang_ky_repo.create({
                "hoc_ky_id": hoc_ky_id,
                "loai_dot": "dang_ky",
                "is_check_toan_truong": True,
                "thoi_gian_bat_dau": parse_datetime(dang_ky_phase.get('startAt')),
                "thoi_gian_ket_thuc": parse_datetime(dang_ky_phase.get('endAt')),
                "gioi_han_tin_chi": 9999,
                "khoa_id": None
            })

        return ServiceResult.ok(created_phases)

