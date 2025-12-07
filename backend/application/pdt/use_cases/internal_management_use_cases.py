from typing import Dict, Any, List
from core.types import ServiceResult
from infrastructure.persistence.models import SinhVien, MonHoc, GiangVien, Users, TaiKhoan
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
import uuid
from datetime import datetime
from django.utils import timezone

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
            tai_khoan = user.tai_khoan if user else None
            
            # Delete in order: SinhVien -> Users -> TaiKhoan
            sv.delete(using='neon')
            if user:
                user.delete(using='neon')
            if tai_khoan:
                tai_khoan.delete(using='neon')
                
            return ServiceResult.ok(None, "Xóa sinh viên thành công")
        except Exception as e:
            return ServiceResult.fail(str(e))

class UpdateSinhVienUseCase:
    def execute(self, id: str, data: Dict[str, Any]) -> ServiceResult:
        try:
            sv = SinhVien.objects.using('neon').select_related('id', 'id__tai_khoan').filter(id=id).first()
            if not sv:
                return ServiceResult.fail("Sinh viên không tồn tại", error_code="NOT_FOUND", status_code=404)
            
            user = sv.id
            tai_khoan = user.tai_khoan if user else None
            
            # Update Users fields
            if 'hoTen' in data or 'ho_ten' in data:
                user.ho_ten = data.get('hoTen') or data.get('ho_ten')
            if 'email' in data:
                user.email = data['email']
            user.updated_at = timezone.now()
            user.save(using='neon')
            
            # Update SinhVien fields
            if 'lop' in data:
                sv.lop = data['lop']
            if 'maKhoa' in data or 'khoaId' in data or 'khoa_id' in data:
                sv.khoa_id = data.get('maKhoa') or data.get('khoaId') or data.get('khoa_id')
            if 'maNganh' in data or 'nganhId' in data or 'nganh_id' in data:
                sv.nganh_id = data.get('maNganh') or data.get('nganhId') or data.get('nganh_id')
            if 'khoaHoc' in data or 'khoa_hoc' in data:
                sv.khoa_hoc = data.get('khoaHoc') or data.get('khoa_hoc')
            if 'ngayNhapHoc' in data or 'ngay_nhap_hoc' in data:
                sv.ngay_nhap_hoc = data.get('ngayNhapHoc') or data.get('ngay_nhap_hoc')
            sv.save(using='neon')
            
            # Update TaiKhoan if needed
            if tai_khoan:
                if 'trangThaiHoatDong' in data or 'trang_thai_hoat_dong' in data:
                    tai_khoan.trang_thai_hoat_dong = data.get('trangThaiHoatDong', data.get('trang_thai_hoat_dong'))
                
                # Update password if provided
                if 'matKhau' in data or 'mat_khau' in data:
                    new_password = data.get('matKhau') or data.get('mat_khau')
                    if new_password:
                        tai_khoan.mat_khau = make_password(new_password)
                
                tai_khoan.updated_at = timezone.now()
                tai_khoan.save(using='neon')
            
            return ServiceResult.ok({
                'id': str(id),
                'maSoSinhVien': sv.ma_so_sinh_vien,
                'hoTen': user.ho_ten,
                'passwordChanged': bool(data.get('matKhau') or data.get('mat_khau'))
            }, "Cập nhật sinh viên thành công")
            
        except Exception as e:
            return ServiceResult.fail(str(e))

class CreateSinhVienUseCase:
    def execute(self, data: Dict[str, Any]) -> ServiceResult:
        try:
            # Validate required fields
            required_fields = ['tenDangNhap', 'matKhau', 'hoTen', 'maSoSinhVien', 'maKhoa']
            for field in required_fields:
                if not data.get(field):
                    return ServiceResult.fail(f"Thiếu thông tin bắt buộc: {field}", error_code="MISSING_PARAMS")
            
            # Check if username or mssv already exists
            if TaiKhoan.objects.using('neon').filter(ten_dang_nhap=data['tenDangNhap']).exists():
                return ServiceResult.fail("Tên đăng nhập đã tồn tại", error_code="DUPLICATE")
            
            if SinhVien.objects.using('neon').filter(ma_so_sinh_vien=data['maSoSinhVien']).exists():
                return ServiceResult.fail("Mã số sinh viên đã tồn tại", error_code="DUPLICATE")
            
            # Create TaiKhoan
            tai_khoan_id = uuid.uuid4()
            tai_khoan = TaiKhoan(
                id=tai_khoan_id,
                ten_dang_nhap=data['tenDangNhap'],
                mat_khau=make_password(data['matKhau']),
                loai_tai_khoan='sinh_vien',
                trang_thai_hoat_dong=data.get('trangThaiHoatDong', True),
                ngay_tao=timezone.now(),
                updated_at=timezone.now()
            )
            tai_khoan.save(using='neon')
            
            # Create Users
            user_id = uuid.uuid4()
            user = Users(
                id=user_id,
                ma_nhan_vien=data['maSoSinhVien'],
                ho_ten=data['hoTen'],
                email=data.get('email', f"{data['maSoSinhVien']}@student.edu.vn"),
                tai_khoan=tai_khoan,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            user.save(using='neon')
            
            # Create SinhVien
            sinh_vien = SinhVien(
                id=user,
                ma_so_sinh_vien=data['maSoSinhVien'],
                lop=data.get('lop'),
                khoa_id=data['maKhoa'],
                nganh_id=data.get('maNganh'),
                khoa_hoc=data.get('khoaHoc'),
                ngay_nhap_hoc=data.get('ngayNhapHoc')
            )
            sinh_vien.save(using='neon')
            
            return ServiceResult.ok({
                'id': str(user_id),
                'maSoSinhVien': data['maSoSinhVien'],
                'hoTen': data['hoTen']
            }, "Tạo sinh viên thành công")
            
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

    def execute_single(self, id: str) -> ServiceResult:
        """Get single MonHoc by ID"""
        try:
            mh = MonHoc.objects.using('neon').select_related('khoa').filter(id=id).first()
            if not mh:
                return ServiceResult.fail("Môn học không tồn tại", error_code="NOT_FOUND", status_code=404)
            
            # Fetch mon_hoc_nganh relations
            mon_hoc_nganh = []
            try:
                from infrastructure.persistence.models import MonHocNganh
                nganh_relations = MonHocNganh.objects.using('neon').select_related('nganh_hoc').filter(mon_hoc_id=id)
                for rel in nganh_relations:
                    mon_hoc_nganh.append({
                        'nganh_id': str(rel.nganh_hoc.id) if rel.nganh_hoc else None,
                        'nganh_hoc': {
                            'id': str(rel.nganh_hoc.id),
                            'ten_nganh': rel.nganh_hoc.ten_nganh
                        } if rel.nganh_hoc else None
                    })
            except Exception:
                pass  # Table might not exist
            
            # Fetch mon_dieu_kien relations
            mon_dieu_kien = []
            try:
                from infrastructure.persistence.models import MonDieuKien
                dk_relations = MonDieuKien.objects.using('neon').select_related('mon_lien_quan').filter(mon_hoc_id=id)
                for dk in dk_relations:
                    mon_dieu_kien.append({
                        'id': str(dk.id),
                        'loai': dk.loai,
                        'bat_buoc': dk.bat_buoc,
                        'mon_lien_quan_id': str(dk.mon_lien_quan.id) if dk.mon_lien_quan else None,
                        'mon_hoc_mon_dieu_kien_mon_lien_quan_idTomon_hoc': {
                            'id': str(dk.mon_lien_quan.id),
                            'ma_mon': dk.mon_lien_quan.ma_mon,
                            'ten_mon': dk.mon_lien_quan.ten_mon
                        } if dk.mon_lien_quan else None
                    })
            except Exception:
                pass  # Table might not exist

            return ServiceResult.ok({
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
                'mon_hoc_nganh': mon_hoc_nganh,
                'mon_dieu_kien_mon_dieu_kien_mon_hoc_idTomon_hoc': mon_dieu_kien
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

    def execute_single(self, giang_vien_id: str) -> ServiceResult:
        """Get single giang vien by ID"""
        try:
            gv = GiangVien.objects.using('neon').select_related('id', 'khoa', 'id__tai_khoan').filter(id=giang_vien_id).first()
            if not gv:
                return ServiceResult.fail("Giảng viên không tồn tại", error_code="NOT_FOUND")
            
            return ServiceResult.ok({
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
        except Exception as e:
            return ServiceResult.fail(str(e))

class DeleteGiangVienUseCase:
    def execute(self, id: str) -> ServiceResult:
        try:
            gv = GiangVien.objects.using('neon').filter(id=id).first()
            if not gv:
                return ServiceResult.fail("Giảng viên không tồn tại", error_code="NOT_FOUND")
            
            user = gv.id
            tai_khoan = user.tai_khoan if user else None
            
            # Delete in order: GiangVien -> Users -> TaiKhoan
            gv.delete(using='neon')
            if user:
                user.delete(using='neon')
            if tai_khoan:
                tai_khoan.delete(using='neon')
                
            return ServiceResult.ok(None, "Xóa giảng viên thành công")
        except Exception as e:
            return ServiceResult.fail(str(e))

class CreateGiangVienUseCase:
    def execute(self, data: Dict[str, Any]) -> ServiceResult:
        try:
            # Validate required fields
            required_fields = ['ten_dang_nhap', 'mat_khau', 'ho_ten', 'khoa_id']
            for field in required_fields:
                if not data.get(field):
                    return ServiceResult.fail(f"Thiếu thông tin bắt buộc: {field}", error_code="MISSING_PARAMS")
            
            # Check if username already exists
            if TaiKhoan.objects.using('neon').filter(ten_dang_nhap=data['ten_dang_nhap']).exists():
                return ServiceResult.fail("Tên đăng nhập đã tồn tại", error_code="DUPLICATE")
            
            # Create TaiKhoan
            tai_khoan_id = uuid.uuid4()
            tai_khoan = TaiKhoan(
                id=tai_khoan_id,
                ten_dang_nhap=data['ten_dang_nhap'],
                mat_khau=make_password(data['mat_khau']),
                loai_tai_khoan='giang_vien',
                trang_thai_hoat_dong=data.get('trang_thai_hoat_dong', True),
                ngay_tao=timezone.now(),
                updated_at=timezone.now()
            )
            tai_khoan.save(using='neon')
            
            # Create Users
            user_id = uuid.uuid4()
            user = Users(
                id=user_id,
                ma_nhan_vien=data['ten_dang_nhap'],
                ho_ten=data['ho_ten'],
                email=data.get('email', f"{data['ten_dang_nhap']}@university.edu.vn"),
                tai_khoan=tai_khoan,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            user.save(using='neon')
            
            # Create GiangVien
            giang_vien = GiangVien(
                id=user,
                khoa_id=data['khoa_id'],
                chuyen_mon=data.get('chuyen_mon'),
                trinh_do=data.get('trinh_do'),
                kinh_nghiem_giang_day=data.get('kinh_nghiem_giang_day')
            )
            giang_vien.save(using='neon')
            
            return ServiceResult.ok({
                'id': str(user_id),
                'ho_ten': data['ho_ten'],
                'ten_dang_nhap': data['ten_dang_nhap']
            }, "Tạo giảng viên thành công")
            
        except Exception as e:
            return ServiceResult.fail(str(e))


class UpdateGiangVienUseCase:
    """
    PUT /api/pdt/giang-vien/<id>
    Update GiangVien info. If mat_khau is provided, also update password.
    """
    def execute(self, giang_vien_id: str, data: Dict[str, Any]) -> ServiceResult:
        try:
            # Find GiangVien
            giang_vien = GiangVien.objects.using('neon').filter(id=giang_vien_id).first()
            if not giang_vien:
                return ServiceResult.fail("Không tìm thấy giảng viên", error_code="NOT_FOUND", status_code=404)
            
            # Get related Users
            user = giang_vien.id  # GiangVien.id is FK to Users
            if not user:
                return ServiceResult.fail("Không tìm thấy thông tin user", error_code="NOT_FOUND", status_code=404)
            
            # Update Users if ho_ten provided
            if data.get('ho_ten'):
                user.ho_ten = data['ho_ten']
                user.updated_at = timezone.now()
                user.save(using='neon')
            
            # Update GiangVien fields
            if data.get('khoa_id'):
                giang_vien.khoa_id = data['khoa_id']
            if 'trinh_do' in data:
                giang_vien.trinh_do = data['trinh_do']
            if 'chuyen_mon' in data:
                giang_vien.chuyen_mon = data['chuyen_mon']
            if 'kinh_nghiem_giang_day' in data:
                giang_vien.kinh_nghiem_giang_day = data['kinh_nghiem_giang_day']
            
            giang_vien.save(using='neon')
            
            # Update password if provided
            if data.get('mat_khau'):
                tai_khoan = user.tai_khoan
                if tai_khoan:
                    tai_khoan.mat_khau = make_password(data['mat_khau'])
                    tai_khoan.updated_at = timezone.now()
                    tai_khoan.save(using='neon')
            
            return ServiceResult.ok({
                'id': str(giang_vien_id),
                'ho_ten': user.ho_ten,
                'khoa_id': str(giang_vien.khoa_id) if giang_vien.khoa_id else None,
                'trinh_do': giang_vien.trinh_do,
                'chuyen_mon': giang_vien.chuyen_mon,
                'kinh_nghiem_giang_day': giang_vien.kinh_nghiem_giang_day,
                'password_changed': bool(data.get('mat_khau'))
            }, "Cập nhật giảng viên thành công")
            
        except Exception as e:
            return ServiceResult.fail(str(e))

