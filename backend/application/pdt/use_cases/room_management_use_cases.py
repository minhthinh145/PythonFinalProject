from typing import List, Optional, Dict, Any
from core.types import ServiceResult
from application.pdt.interfaces.repositories import IPhongHocRepository

class GetAvailablePhongHocUseCase:
    def __init__(self, phong_repo: IPhongHocRepository):
        self.phong_repo = phong_repo

    def execute(self) -> ServiceResult:
        try:
            rooms = self.phong_repo.get_available_rooms()
            mapped_rooms = [
                {
                    'id': str(r['id']),
                    'maPhong': r['ma_phong'],
                    'sucChua': r['suc_chua'],
                    'daSuDung': r['da_dc_su_dung'],
                    'khoaId': str(r['khoa_id']) if r['khoa_id'] else None,
                    'coSoId': str(r['co_so_id']) if 'co_so_id' in r and r['co_so_id'] else None,
                    'tenCoSo': r.get('co_so__ten_co_so')
                } for r in rooms
            ]
            return ServiceResult.ok(mapped_rooms)
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetPhongHocByKhoaUseCase:
    def __init__(self, phong_repo: IPhongHocRepository):
        self.phong_repo = phong_repo

    def execute(self, khoa_id: str) -> ServiceResult:
        try:
            rooms = self.phong_repo.get_by_khoa(khoa_id)
            mapped_rooms = [
                {
                    'id': str(r['id']),
                    'maPhong': r['ma_phong'],
                    'sucChua': r['suc_chua'],
                    'daSuDung': r['da_dc_su_dung'],
                    'khoaId': str(r['khoa_id']) if r['khoa_id'] else None,
                    'coSoId': str(r['co_so_id']) if 'co_so_id' in r and r['co_so_id'] else None,
                    'tenCoSo': r.get('co_so__ten_co_so')
                } for r in rooms
            ]
            return ServiceResult.ok(mapped_rooms)
        except Exception as e:
            return ServiceResult.fail(str(e))

class AssignPhongToKhoaUseCase:
    def __init__(self, phong_repo: IPhongHocRepository):
        self.phong_repo = phong_repo

    def execute(self, phong_id: str, khoa_id: str) -> ServiceResult:
        try:
            if not phong_id or not khoa_id:
                return ServiceResult.fail("Thiếu thông tin", error_code="MISSING_PARAMS")
            
            success = self.phong_repo.assign_to_khoa(phong_id, khoa_id)
            if success:
                return ServiceResult.ok(None, "Gán phòng thành công")
            return ServiceResult.fail("Gán phòng thất bại", error_code="FAILED")
        except Exception as e:
            return ServiceResult.fail(str(e))

class UnassignPhongFromKhoaUseCase:
    def __init__(self, phong_repo: IPhongHocRepository):
        self.phong_repo = phong_repo

    def execute(self, phong_id: str) -> ServiceResult:
        try:
            if not phong_id:
                return ServiceResult.fail("Thiếu thông tin", error_code="MISSING_PARAMS")
            
            success = self.phong_repo.unassign_from_khoa(phong_id)
            if success:
                return ServiceResult.ok(None, "Hủy gán phòng thành công")
            return ServiceResult.fail("Hủy gán phòng thất bại", error_code="FAILED")
        except Exception as e:
            return ServiceResult.fail(str(e))
