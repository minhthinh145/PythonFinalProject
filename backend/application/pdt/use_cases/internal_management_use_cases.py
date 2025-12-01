from typing import Dict, Any, List
from core.types import ServiceResult
from infrastructure.persistence.models import SinhVien, MonHoc, GiangVien, Users
from django.core.paginator import Paginator

class GetDanhSachSinhVienUseCase:
    def execute(self, page=1, page_size=10000) -> ServiceResult:
        try:
            qs = SinhVien.objects.using('neon').select_related('id', 'khoa', 'nganh').all().order_by('ma_so_sinh_vien')
            paginator = Paginator(qs, page_size)
            page_obj = paginator.get_page(page)
            
            items = []
            for sv in page_obj:
                items.append({
                    'id': str(sv.id.id),
                    'maSoSinhVien': sv.ma_so_sinh_vien,
                    'hoTen': sv.id.ho_ten,
                    'lop': sv.lop,
                    'tenKhoa': sv.khoa.ten_khoa if sv.khoa else "",
                    'tenNganh': sv.nganh.ten_nganh if sv.nganh else "",
                    'khoaHoc': sv.khoa_hoc,
                    'trangThaiHoatDong': sv.id.tai_khoan.trang_thai_hoat_dong if sv.id.tai_khoan else True,
                    'ngayNhapHoc': sv.ngay_nhap_hoc,
                    'email': sv.id.email
                })
                
            return ServiceResult.ok({
                'items': items,
                'total': paginator.count,
                'page': page,
                'pageSize': page_size
            })
        except Exception as e:
            return ServiceResult.fail(str(e))

class DeleteSinhVienUseCase:
    def execute(self, id: str) -> ServiceResult:
        try:
            sv = SinhVien.objects.using('neon').filter(id=id).first()
            if not sv:
                return ServiceResult.fail("Sinh viên không tồn tại", error_code="NOT_FOUND")
            
            user = sv.id
            sv.delete()
            if user:
                user.delete()
                
            return ServiceResult.ok(None)
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetDanhSachMonHocUseCase:
    def execute(self, page=1, page_size=10000) -> ServiceResult:
        try:
            qs = MonHoc.objects.using('neon').select_related('khoa').all().order_by('ma_mon')
            paginator = Paginator(qs, page_size)
            page_obj = paginator.get_page(page)
            
            items = []
            for mh in page_obj:

                items.append({
                    'id': str(mh.id),
                    'ma_mon': mh.ma_mon,
                    'ten_mon': mh.ten_mon,
                    'so_tin_chi': mh.so_tin_chi,
                    'khoa_id': str(mh.khoa.id) if mh.khoa else None,
                    'loai_mon': mh.loai_mon,
                    'la_mon_chung': mh.la_mon_chung,
                    'thu_tu_hoc': mh.thu_tu_hoc,
                    'khoa': {
                        'id': str(mh.khoa.id),
                        'ten_khoa': mh.khoa.ten_khoa
                    } if mh.khoa else None,
                    # Assuming mon_hoc_nganh relation exists or needs to be fetched
                    # For now returning empty list or fetching if relation exists
                    'mon_hoc_nganh': [] 
                })
                
            return ServiceResult.ok({
                'items': items,
                'total': paginator.count,
                'page': page,
                'pageSize': page_size
            })
        except Exception as e:
            return ServiceResult.fail(str(e))

class DeleteMonHocUseCase:
    def execute(self, id: str) -> ServiceResult:
        try:
            count, _ = MonHoc.objects.using('neon').filter(id=id).delete()
            if count > 0:
                return ServiceResult.ok(None)
            return ServiceResult.fail("Môn học không tồn tại", error_code="NOT_FOUND")
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetDanhSachGiangVienUseCase:
    def execute(self, page=1, page_size=10000) -> ServiceResult:
        try:
            qs = GiangVien.objects.using('neon').select_related('id', 'khoa', 'id__tai_khoan').all().order_by('id__ho_ten')
            paginator = Paginator(qs, page_size)
            page_obj = paginator.get_page(page)
            
            items = []
            for gv in page_obj:
                items.append({
                    'id': str(gv.id.id),
                    'khoa_id': str(gv.khoa.id) if gv.khoa else None,
                    'trinh_do': gv.trinh_do,
                    'chuyen_mon': gv.chuyen_mon,
                    'kinh_nghiem_giang_day': gv.kinh_nghiem_giang_day,
                    'users': {
                        'id': str(gv.id.id),
                        'ho_ten': gv.id.ho_ten,
                        'ma_nhan_vien': gv.id.ma_nhan_vien,
                        'tai_khoan': {
                            'ten_dang_nhap': gv.id.tai_khoan.ten_dang_nhap if gv.id.tai_khoan else ""
                        } if gv.id.tai_khoan else None
                    },
                    'khoa': {
                        'id': str(gv.khoa.id),
                        'ten_khoa': gv.khoa.ten_khoa
                    } if gv.khoa else None
                })
                
            return ServiceResult.ok({
                'items': items,
                'total': paginator.count,
                'page': page,
                'pageSize': page_size
            })
        except Exception as e:
            return ServiceResult.fail(str(e))

class DeleteGiangVienUseCase:
    def execute(self, id: str) -> ServiceResult:
        try:
            gv = GiangVien.objects.using('neon').filter(id=id).first()
            if not gv:
                return ServiceResult.fail("Giảng viên không tồn tại", error_code="NOT_FOUND")
            
            user = gv.id
            gv.delete()
            if user:
                user.delete()
                
            return ServiceResult.ok(None)
        except Exception as e:
            return ServiceResult.fail(str(e))
