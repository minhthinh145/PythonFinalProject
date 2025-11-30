from django.db.models import Count, Sum, Q
from core.types import ServiceResult
from infrastructure.persistence.models import (
    DangKyHocPhan, LopHocPhan, HocPhi, Khoa, NganhHoc, GiangVien
)

class GetOverviewStatsUseCase:
    def execute(self, hoc_ky_id, khoa_id=None, nganh_id=None):
        try:
            # Base filters
            dk_filter = Q(lop_hoc_phan__hoc_phan__id_hoc_ky_id=hoc_ky_id)
            lhp_filter = Q(hoc_phan__id_hoc_ky_id=hoc_ky_id)
            hp_filter = Q(hoc_ky_id=hoc_ky_id)

            if khoa_id:
                dk_filter &= Q(sinh_vien__khoa_id=khoa_id)
                # LHP doesn't directly link to Khoa easily without joining through MonHoc or GiangVien, 
                # but usually reports filter by Student's Khoa for registration stats.
                # For LHP count, we might filter by MonHoc's Khoa.
                lhp_filter &= Q(hoc_phan__mon_hoc__khoa_id=khoa_id)
                hp_filter &= Q(sinh_vien__khoa_id=khoa_id)
            
            if nganh_id:
                dk_filter &= Q(sinh_vien__nganh_id=nganh_id)
                hp_filter &= Q(sinh_vien__nganh_id=nganh_id)
                # LHP doesn't belong to a Nganh directly.

            # 1. SV Unique
            sv_unique = DangKyHocPhan.objects.using('neon').filter(dk_filter).values('sinh_vien').distinct().count()

            # 2. So Dang Ky
            so_dang_ky = DangKyHocPhan.objects.using('neon').filter(dk_filter).count()

            # 3. So Lop Hoc Phan
            so_lop_hoc_phan = LopHocPhan.objects.using('neon').filter(lhp_filter).count()

            # 4. Tai Chinh
            # Ky vong: Tong hoc phi phai thu
            ky_vong = HocPhi.objects.using('neon').filter(hp_filter).aggregate(total=Sum('tong_hoc_phi'))['total'] or 0
            
            # Thuc thu: Tong hoc phi da thanh toan
            # Assuming 'DA_THANH_TOAN' is the status. 
            # If partial payment exists, logic might be more complex, but for now assume full payment.
            thuc_thu = HocPhi.objects.using('neon').filter(hp_filter, trang_thai_thanh_toan='DA_THANH_TOAN').aggregate(total=Sum('tong_hoc_phi'))['total'] or 0

            return ServiceResult.ok({
                'svUnique': sv_unique,
                'soDangKy': so_dang_ky,
                'soLopHocPhan': so_lop_hoc_phan,
                'taiChinh': {
                    'thuc_thu': float(thuc_thu),
                    'ky_vong': float(ky_vong)
                },
                'ketLuan': f"Tổng quan: {sv_unique} sinh viên đã đăng ký {so_dang_ky} lượt học phần."
            })
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetKhoaStatsUseCase:
    def execute(self, hoc_ky_id):
        try:
            # Group by Khoa
            stats = DangKyHocPhan.objects.using('neon')\
                .filter(lop_hoc_phan__hoc_phan__id_hoc_ky_id=hoc_ky_id)\
                .values('sinh_vien__khoa__ten_khoa')\
                .annotate(so_dang_ky=Count('id'))\
                .order_by('-so_dang_ky')

            data = [
                {
                    'ten_khoa': item['sinh_vien__khoa__ten_khoa'],
                    'so_dang_ky': item['so_dang_ky']
                }
                for item in stats
            ]

            return ServiceResult.ok({
                'data': data,
                'ketLuan': "Thống kê số lượng đăng ký theo từng khoa."
            })
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetNganhStatsUseCase:
    def execute(self, hoc_ky_id, khoa_id=None):
        try:
            filters = Q(lop_hoc_phan__hoc_phan__id_hoc_ky_id=hoc_ky_id)
            if khoa_id:
                filters &= Q(sinh_vien__khoa_id=khoa_id)

            stats = DangKyHocPhan.objects.using('neon')\
                .filter(filters)\
                .values('sinh_vien__nganh__ten_nganh')\
                .annotate(so_dang_ky=Count('id'))\
                .order_by('-so_dang_ky')

            data = [
                {
                    'ten_nganh': item['sinh_vien__nganh__ten_nganh'] or 'Chưa phân ngành',
                    'so_dang_ky': item['so_dang_ky']
                }
                for item in stats
            ]

            return ServiceResult.ok({
                'data': data,
                'ketLuan': "Thống kê số lượng đăng ký theo ngành."
            })
        except Exception as e:
            return ServiceResult.fail(str(e))

class GetGiangVienStatsUseCase:
    def execute(self, hoc_ky_id, khoa_id=None):
        try:
            filters = Q(hoc_phan__id_hoc_ky_id=hoc_ky_id)
            if khoa_id:
                filters &= Q(giang_vien__khoa_id=khoa_id)

            stats = LopHocPhan.objects.using('neon')\
                .filter(filters)\
                .values('giang_vien__id__ho_ten')\
                .annotate(so_lop=Count('id'))\
                .order_by('-so_lop')

            data = [
                {
                    'ho_ten': item['giang_vien__id__ho_ten'] or 'Chưa phân công',
                    'so_lop': item['so_lop']
                }
                for item in stats
            ]

            return ServiceResult.ok({
                'data': data,
                'ketLuan': "Thống kê số lượng lớp học phần theo giảng viên."
            })
        except Exception as e:
            return ServiceResult.fail(str(e))
