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
            is_toan_truong = data.get('isToanTruong', False)

            if not hoc_ky_id:
                return ServiceResult.fail("Thiếu thông tin bắt buộc (hocKyId)", error_code="MISSING_PARAMS")

            if is_toan_truong:
                # Toàn trường - single record
                start_at = data.get('thoiGianBatDau')
                end_at = data.get('thoiGianKetThuc')
                
                if not all([start_at, end_at]):
                    return ServiceResult.fail("Thiếu thông tin bắt buộc (thoiGianBatDau, thoiGianKetThuc)", error_code="MISSING_PARAMS")

                all_dots = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'ghi_danh')
                
                # DELETE only ghi_danh khoa-specific records when switching to toàn trường
                for dot in all_dots:
                    if dot.khoa_id is not None and dot.loai_dot == 'ghi_danh':
                        self.dot_dang_ky_repo.delete(dot.id)
                
                existing_dot = next((d for d in all_dots if d.khoa_id is None), None)

                if existing_dot:
                    self.dot_dang_ky_repo.update(existing_dot.id, {
                        'thoi_gian_bat_dau': start_at,
                        'thoi_gian_ket_thuc': end_at,
                        'is_check_toan_truong': True,
                        'khoa_id': None
                    })
                else:
                    self.dot_dang_ky_repo.create({
                        'id': uuid.uuid4(),
                        'hoc_ky_id': hoc_ky_id,
                        'khoa_id': None,
                        'loai_dot': 'ghi_danh',
                        'thoi_gian_bat_dau': start_at,
                        'thoi_gian_ket_thuc': end_at,
                        'is_check_toan_truong': True
                    })
            else:
                # Theo khoa - batch update
                dot_theo_khoa = data.get('dotTheoKhoa', [])
                
                if not dot_theo_khoa:
                    return ServiceResult.fail("Thiếu thông tin dotTheoKhoa", error_code="MISSING_PARAMS")

                all_dots = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'ghi_danh')
                
                # DELETE only ghi_danh toàn trường record when switching to theo khoa
                for dot in all_dots:
                    if dot.khoa_id is None and dot.loai_dot == 'ghi_danh':
                        self.dot_dang_ky_repo.delete(dot.id)

                for khoa_dot in dot_theo_khoa:
                    khoa_id = khoa_dot.get('khoaId')
                    start_at = khoa_dot.get('thoiGianBatDau')
                    end_at = khoa_dot.get('thoiGianKetThuc')
                    
                    if not all([khoa_id, start_at, end_at]):
                        continue  # Skip invalid entries
                    
                    existing_dot = next((d for d in all_dots if str(d.khoa_id) == khoa_id), None)

                    if existing_dot:
                        self.dot_dang_ky_repo.update(existing_dot.id, {
                            'thoi_gian_bat_dau': start_at,
                            'thoi_gian_ket_thuc': end_at,
                            'is_check_toan_truong': False,
                            'khoa_id': khoa_id
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
            # Get only 'ghi_danh' type registration periods
            dots = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'ghi_danh')
            return ServiceResult.ok([
                {
                    'id': str(d.id),
                    'hocKyId': str(d.hoc_ky_id),
                    'loaiDot': d.loai_dot,
                    'khoaId': str(d.khoa_id) if d.khoa_id else None,
                    'tenKhoa': d.khoa.ten_khoa if d.khoa else None,
                    'thoiGianBatDau': d.thoi_gian_bat_dau.isoformat() if d.thoi_gian_bat_dau else None,
                    'thoiGianKetThuc': d.thoi_gian_ket_thuc.isoformat() if d.thoi_gian_ket_thuc else None,
                    'hanHuyDen': d.han_huy_den.isoformat() if d.han_huy_den else None,
                    'gioiHanTinChi': d.gioi_han_tin_chi,
                    'isCheckToanTruong': d.is_check_toan_truong,
                } for d in dots
            ])
        except Exception as e:
            return ServiceResult.fail(str(e))

class UpdateDotDangKyUseCase:
    def __init__(self, dot_dang_ky_repo: IDotDangKyRepository):
        self.dot_dang_ky_repo = dot_dang_ky_repo

    def execute(self, data: dict) -> ServiceResult:
        try:
            hoc_ky_id = data.get('hocKyId')
            is_toan_truong = data.get('isToanTruong', False)
            
            if not hoc_ky_id:
                return ServiceResult.fail("Thiếu hocKyId", error_code="MISSING_PARAMS")

            if is_toan_truong:
                # Handle single record for whole school (toàn trường)
                thoi_gian_bat_dau = data.get('thoiGianBatDau')
                thoi_gian_ket_thuc = data.get('thoiGianKetThuc')
                
                if not all([thoi_gian_bat_dau, thoi_gian_ket_thuc]):
                    return ServiceResult.fail("Thiếu thông tin bắt buộc (thoiGianBatDau, thoiGianKetThuc)", error_code="MISSING_PARAMS")
                
                # DELETE only dang_ky khoa-specific records when switching to toàn trường
                existing_dots = self.dot_dang_ky_repo.find_by_hoc_ky(hoc_ky_id)
                for dot in existing_dots:
                    if dot.khoa_id is not None and dot.loai_dot == 'dang_ky':
                        self.dot_dang_ky_repo.delete(dot.id)
                
                update_data = {
                    'hoc_ky_id': hoc_ky_id,
                    'loai_dot': 'dang_ky',
                    'thoi_gian_bat_dau': thoi_gian_bat_dau,
                    'thoi_gian_ket_thuc': thoi_gian_ket_thuc,
                    'han_huy_den': data.get('hanHuyDen'),
                    'gioi_han_tin_chi': data.get('gioiHanTinChi'),
                    'is_check_toan_truong': True,
                    'khoa_id': None
                }
                
                # Check if record exists
                dot_toan_truong_id = data.get('dotToanTruongId')
                if dot_toan_truong_id:
                    self.dot_dang_ky_repo.update(dot_toan_truong_id, update_data)
                else:
                    # Find existing record with khoa_id=None
                    existing_dots = self.dot_dang_ky_repo.find_by_hoc_ky(hoc_ky_id)
                    existing_toan_truong = next((d for d in existing_dots if d.khoa_id is None), None)
                    if existing_toan_truong:
                        self.dot_dang_ky_repo.update(existing_toan_truong.id, update_data)
                    else:
                        self.dot_dang_ky_repo.create(update_data)
            else:
                # Handle batch records for each khoa (theo khoa)
                dot_theo_khoa = data.get('dotTheoKhoa', [])
                
                if not dot_theo_khoa:
                    return ServiceResult.fail("Thiếu thông tin dotTheoKhoa khi isToanTruong = false", error_code="MISSING_PARAMS")
                
                # DELETE only dang_ky toàn trường record when switching to theo khoa
                existing_dots = self.dot_dang_ky_repo.find_by_hoc_ky(hoc_ky_id)
                for dot in existing_dots:
                    if dot.khoa_id is None and dot.loai_dot == 'dang_ky':
                        self.dot_dang_ky_repo.delete(dot.id)
                
                for khoa_dot in dot_theo_khoa:
                    khoa_id = khoa_dot.get('khoaId')
                    thoi_gian_bat_dau = khoa_dot.get('thoiGianBatDau')
                    thoi_gian_ket_thuc = khoa_dot.get('thoiGianKetThuc')
                    
                    if not all([khoa_id, thoi_gian_bat_dau, thoi_gian_ket_thuc]):
                        continue  # Skip invalid entries
                    
                    update_data = {
                        'hoc_ky_id': hoc_ky_id,
                        'loai_dot': 'dang_ky',
                        'thoi_gian_bat_dau': thoi_gian_bat_dau,
                        'thoi_gian_ket_thuc': thoi_gian_ket_thuc,
                        'han_huy_den': khoa_dot.get('hanHuyDen'),
                        'gioi_han_tin_chi': khoa_dot.get('gioiHanTinChi'),
                        'is_check_toan_truong': False,
                        'khoa_id': khoa_id
                    }
                    
                    # Check if record exists for this khoa
                    dot_khoa_id = khoa_dot.get('id')
                    if dot_khoa_id:
                        self.dot_dang_ky_repo.update(dot_khoa_id, update_data)
                    else:
                        # Find existing record with this khoa_id
                        existing_dots = self.dot_dang_ky_repo.find_by_hoc_ky(hoc_ky_id)
                        existing_khoa = next((d for d in existing_dots if d.khoa_id == khoa_id), None)
                        if existing_khoa:
                            self.dot_dang_ky_repo.update(existing_khoa.id, update_data)
                        else:
                            self.dot_dang_ky_repo.create(update_data)

            # Return updated list
            updated_dots = self.dot_dang_ky_repo.find_by_hoc_ky(hoc_ky_id)
            result_data = [
                {
                    "id": str(dot.id),
                    "hocKyId": str(dot.hoc_ky_id),
                    "loaiDot": dot.loai_dot,
                    "thoiGianBatDau": dot.thoi_gian_bat_dau.isoformat() if dot.thoi_gian_bat_dau else None,
                    "thoiGianKetThuc": dot.thoi_gian_ket_thuc.isoformat() if dot.thoi_gian_ket_thuc else None,
                    "hanHuyDen": dot.han_huy_den.isoformat() if dot.han_huy_den else None,
                    "gioiHanTinChi": dot.gioi_han_tin_chi,
                    "isCheckToanTruong": dot.is_check_toan_truong,
                    "khoaId": str(dot.khoa_id) if dot.khoa_id else None,
                    "tenKhoa": dot.khoa.ten_khoa if dot.khoa else None
                }
                for dot in updated_dots
            ]
            
            return ServiceResult.ok(result_data, "Cập nhật đợt đăng ký thành công")
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetDotDangKyByHocKyUseCase:
    def __init__(self, dot_dang_ky_repo: IDotDangKyRepository):
        self.dot_dang_ky_repo = dot_dang_ky_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult:
        try:
            # Get only 'dang_ky' type registration periods
            dots = self.dot_dang_ky_repo.find_by_hoc_ky_and_loai(hoc_ky_id, 'dang_ky')
            
            return ServiceResult.ok([
                {
                    'id': str(d.id),
                    'hocKyId': str(d.hoc_ky_id),
                    'loaiDot': d.loai_dot,
                    'thoiGianBatDau': d.thoi_gian_bat_dau.isoformat() if d.thoi_gian_bat_dau else None,
                    'thoiGianKetThuc': d.thoi_gian_ket_thuc.isoformat() if d.thoi_gian_ket_thuc else None,
                    'hanHuyDen': d.han_huy_den.isoformat() if d.han_huy_den else None,
                    'gioiHanTinChi': d.gioi_han_tin_chi,
                    'isCheckToanTruong': d.is_check_toan_truong,
                    'khoaId': str(d.khoa_id) if d.khoa_id else None,
                    'tenKhoa': d.khoa.ten_khoa if d.khoa else None
                } for d in dots
            ])
        except Exception as e:
            return ServiceResult.fail(str(e))
