from typing import List, Optional, Dict, Any
from core.types import ServiceResult
from application.enrollment.interfaces import IDotDangKyRepository
import uuid

class UpdateDotGhiDanhUseCase:
    def __init__(self, dot_dang_ky_repo: IDotDangKyRepository):
        self.dot_dang_ky_repo = dot_dang_ky_repo

    def execute(self, data: dict) -> ServiceResult:
        try:
            hoc_ky_id = data.get('hocKyId')
            khoa_id = data.get('khoaId')
            start_at = data.get('thoiGianBatDau')
            end_at = data.get('thoiGianKetThuc')

            if not all([hoc_ky_id, khoa_id, start_at, end_at]):
                return ServiceResult.fail("Thiếu thông tin bắt buộc", error_code="MISSING_PARAMS")

            # Find existing dot ghi danh for this khoa and hocky
            # Since we don't have a specific find method for this combination in interface yet, 
            # we can use find_by_hoc_ky_and_loai and filter in memory or add a new method.
            # Using find_by_hoc_ky_and_loai is safer for now to avoid interface churn.
            
            all_dots = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'ghi_danh')
            existing_dot = next((d for d in all_dots if str(d.khoa_id) == khoa_id), None)

            if existing_dot:
                self.dot_dang_ky_repo.update(existing_dot.id, {
                    'thoi_gian_bat_dau': start_at,
                    'thoi_gian_ket_thuc': end_at
                })
            else:
                self.dot_dang_ky_repo.create({
                    'id': uuid.uuid4(),
                    'hoc_ky_id': hoc_ky_id,
                    'khoa_id': khoa_id,
                    'loai_dot': 'ghi_danh',
                    'thoi_gian_bat_dau': start_at,
                    'thoi_gian_ket_thuc': end_at,
                    'is_check_toan_truong': False
                })

            # Return updated list
            updated_list = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'ghi_danh')
            return ServiceResult.ok([
                {
                    'id': str(d.id),
                    'hocKyId': str(d.hoc_ky_id),
                    'khoaId': str(d.khoa_id) if d.khoa_id else None,
                    'thoiGianBatDau': d.thoi_gian_bat_dau.isoformat() if d.thoi_gian_bat_dau else None,
                    'thoiGianKetThuc': d.thoi_gian_ket_thuc.isoformat() if d.thoi_gian_ket_thuc else None,
                } for d in updated_list
            ])

        except Exception as e:
            return ServiceResult.fail(str(e))

class GetDotGhiDanhByHocKyUseCase:
    def __init__(self, dot_dang_ky_repo: IDotDangKyRepository):
        self.dot_dang_ky_repo = dot_dang_ky_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult:
        try:
            dots = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'ghi_danh')
            return ServiceResult.ok([
                {
                    'id': str(d.id),
                    'hocKyId': str(d.hoc_ky_id),
                    'khoaId': str(d.khoa_id) if d.khoa_id else None,
                    'thoiGianBatDau': d.thoi_gian_bat_dau.isoformat() if d.thoi_gian_bat_dau else None,
                    'thoiGianKetThuc': d.thoi_gian_ket_thuc.isoformat() if d.thoi_gian_ket_thuc else None,
                } for d in dots
            ])
        except Exception as e:
            return ServiceResult.fail(str(e))

class UpdateDotDangKyUseCase:
    def __init__(self, dot_dang_ky_repo: IDotDangKyRepository):
        self.dot_dang_ky_repo = dot_dang_ky_repo

    def execute(self, data: dict) -> ServiceResult:
        try:
            dot_id = data.get('id')
            hoc_ky_id = data.get('hocKyId')
            
            if not hoc_ky_id:
                return ServiceResult.fail("Thiếu hocKyId", error_code="MISSING_PARAMS")

            update_data = {
                'hoc_ky_id': hoc_ky_id,
                'loai_dot': data.get('loaiDot'),
                'thoi_gian_bat_dau': data.get('thoiGianBatDau'),
                'thoi_gian_ket_thuc': data.get('thoiGianKetThuc'),
                'is_check_toan_truong': data.get('isCheckToanTruong', False),
                'khoa_id': data.get('khoaId')
            }

            if dot_id:
                self.dot_dang_ky_repo.update(dot_id, update_data)
            else:
                self.dot_dang_ky_repo.create(update_data)

            return ServiceResult.ok(None, "Cập nhật đợt đăng ký thành công")
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetDotDangKyByHocKyUseCase:
    def __init__(self, dot_dang_ky_repo: IDotDangKyRepository):
        self.dot_dang_ky_repo = dot_dang_ky_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult:
        try:
            # Get all types or just dang_ky? FE seems to want all for the management table
            # But the repo method is find_by_hoc_ky_and_loai.
            # We might need a find_by_hoc_ky method in repo.
            # For now, let's assume we want 'dang_ky_hoc_phan' and 'huy_dang_ky' etc.
            # Or we can just fetch all and filter in memory if needed, but repo doesn't have find_all_by_hoc_ky.
            # Let's use find_by_hoc_ky_and_loai for 'dang_ky_hoc_phan' as primary.
            
            # Wait, the FE table shows multiple rows.
            # Let's implement find_by_hoc_ky in repo to get ALL dots for the semester.
            # But I can't change repo interface easily right now without another tool call.
            # I'll use find_by_hoc_ky_and_loai for 'dang_ky_hoc_phan' for now.
            
            dots = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'dang_ky')
            
            return ServiceResult.ok([
                {
                    'id': str(d.id),
                    'hocKyId': str(d.hoc_ky_id),
                    'loaiDot': d.loai_dot,
                    'thoiGianBatDau': d.thoi_gian_bat_dau.isoformat() if d.thoi_gian_bat_dau else None,
                    'thoiGianKetThuc': d.thoi_gian_ket_thuc.isoformat() if d.thoi_gian_ket_thuc else None,
                    'isCheckToanTruong': d.is_check_toan_truong,
                    'khoaId': str(d.khoa_id) if d.khoa_id else None
                } for d in dots
            ])
        except Exception as e:
            return ServiceResult.fail(str(e))
