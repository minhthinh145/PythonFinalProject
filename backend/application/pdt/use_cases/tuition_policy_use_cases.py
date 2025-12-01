from typing import List, Optional, Dict, Any
from core.types import ServiceResult
from application.pdt.interfaces.repositories import IChinhSachHocPhiRepository
import uuid
from datetime import date

class GetChinhSachTinChiUseCase:
    def __init__(self, chinh_sach_repo: IChinhSachHocPhiRepository):
        self.chinh_sach_repo = chinh_sach_repo

    def execute(self) -> ServiceResult:
        try:
            policies_data = self.chinh_sach_repo.get_all()
            # Map flat dict to nested structure expected by Frontend
            policies = []
            for p in policies_data:
                policies.append({
                    'id': str(p['id']),
                    'hocKyId': str(p['hoc_ky_id']) if p['hoc_ky_id'] else None,
                    'khoaId': str(p['khoa_id']) if p['khoa_id'] else None,
                    'nganhId': str(p['nganh_id']) if p['nganh_id'] else None,
                    'phiMoiTinChi': float(p['phi_moi_tin_chi']),
                    'ngayHieuLuc': p['ngay_hieu_luc'],
                    'ngayHetHieuLuc': p['ngay_het_hieu_luc'],
                    'hocKy': {
                        'tenHocKy': p['hoc_ky__ten_hoc_ky']
                    } if p['hoc_ky__ten_hoc_ky'] else None,
                    'khoa': {
                        'tenKhoa': p['khoa__ten_khoa']
                    } if p['khoa__ten_khoa'] else None,
                    'nganhHoc': {
                        'tenNganh': p['nganh__ten_nganh']
                    } if p['nganh__ten_nganh'] else None
                })
            return ServiceResult.ok(policies)
        except Exception as e:
            return ServiceResult.fail(str(e))

class CreateChinhSachTinChiUseCase:
    def __init__(self, chinh_sach_repo: IChinhSachHocPhiRepository):
        self.chinh_sach_repo = chinh_sach_repo

    def execute(self, data: dict) -> ServiceResult:
        try:
            # Validate required fields
            required = ['hocKyId', 'phiMoiTinChi', 'ngayHieuLuc']
            if not all(k in data for k in required):
                return ServiceResult.fail("Thiếu thông tin bắt buộc", error_code="MISSING_PARAMS")

            # Check if policy exists for this combination (if specific logic needed)
            # For now, just create
            
            new_policy = {
                'id': uuid.uuid4(),
                'hoc_ky_id': data['hocKyId'],
                'khoa_id': data.get('khoaId'),
                'nganh_id': data.get('nganhId'),
                'phi_moi_tin_chi': data['phiMoiTinChi'],
                'ngay_hieu_luc': data['ngayHieuLuc'],
                'ngay_het_hieu_luc': data.get('ngayHetHieuLuc')
            }
            
            created = self.chinh_sach_repo.create(new_policy)
            if created:
                return ServiceResult.ok({
                    'id': str(created.id),
                    'hocKyId': str(created.hoc_ky_id),
                    'khoaId': str(created.khoa_id) if created.khoa_id else None,
                    'nganhId': str(created.nganh_id) if created.nganh_id else None,
                    'phiMoiTinChi': float(created.phi_moi_tin_chi),
                    'ngayHieuLuc': created.ngay_hieu_luc.isoformat() if hasattr(created.ngay_hieu_luc, 'isoformat') else str(created.ngay_hieu_luc),
                    'ngayHetHieuLuc': created.ngay_het_hieu_luc.isoformat() if created.ngay_het_hieu_luc and hasattr(created.ngay_het_hieu_luc, 'isoformat') else (str(created.ngay_het_hieu_luc) if created.ngay_het_hieu_luc else None)
                })
            return ServiceResult.fail("Tạo chính sách thất bại", error_code="FAILED")
        except Exception as e:
            return ServiceResult.fail(str(e))

class UpdateChinhSachTinChiUseCase:
    def __init__(self, chinh_sach_repo: IChinhSachHocPhiRepository):
        self.chinh_sach_repo = chinh_sach_repo

    def execute(self, id: str, data: dict) -> ServiceResult:
        try:
            success = self.chinh_sach_repo.update(id, {
                'phi_moi_tin_chi': data.get('phiMoiTinChi'),
                'ngay_hieu_luc': data.get('ngayHieuLuc'),
                'ngay_het_hieu_luc': data.get('ngayHetHieuLuc')
            })
            if success:
                return ServiceResult.ok(None, "Cập nhật thành công")
            return ServiceResult.fail("Cập nhật thất bại", error_code="FAILED")
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetDanhSachNganhChuaCoChinhSachUseCase:
    def __init__(self, chinh_sach_repo: IChinhSachHocPhiRepository):
        self.chinh_sach_repo = chinh_sach_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult:
        # This might require a specific repo method or logic to compare all majors vs existing policies
        # For MVP, maybe skip or implement basic list
        return ServiceResult.ok([])

class TinhHocPhiHangLoatUseCase:
    def __init__(self, chinh_sach_repo: IChinhSachHocPhiRepository):
        self.chinh_sach_repo = chinh_sach_repo

    def execute(self, hoc_ky_id: str) -> ServiceResult:
        try:
            count = self.chinh_sach_repo.calculate_tuition_bulk(hoc_ky_id)
            return ServiceResult.ok({'count': count}, f"Đã tính học phí cho {count} sinh viên")
        except Exception as e:
            return ServiceResult.fail(str(e))
