"""
Infrastructure Layer - Course Registration Repository Implementations
"""
from typing import Optional, List, Any
from django.db.models import F
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository,
    ILichSuDangKyRepository,
    ILichHocDinhKyRepository,
    IHocPhiRepository
)
from infrastructure.persistence.models import (
    LopHocPhan,
    DangKyHocPhan,
    DangKyTkb,
    LichSuDangKy,
    ChiTietLichSuDangKy,
    LichHocDinhKy,
    HocPhi,
    TaiLieu
)
import uuid

class LopHocPhanRepository(ILopHocPhanRepository):
    def find_by_id(self, id: str) -> Optional[LopHocPhan]:
        try:
            return LopHocPhan.objects.using('neon').get(id=id)
        except LopHocPhan.DoesNotExist:
            return None

    def update_so_luong(self, id: str, amount: int) -> None:
        LopHocPhan.objects.using('neon').filter(id=id).update(
            so_luong_hien_tai=F('so_luong_hien_tai') + amount
        )

    def find_all_by_hoc_ky(self, hoc_ky_id: str) -> List[LopHocPhan]:
        return list(LopHocPhan.objects.using('neon').filter(
            hoc_phan__id_hoc_ky=hoc_ky_id
        ).select_related(
            'hoc_phan',
            'hoc_phan__mon_hoc',
            'giang_vien',
            'giang_vien__id'
        ).prefetch_related(
            'lichhocdinhky_set',
            'lichhocdinhky_set__phong'
        ).order_by('hoc_phan__mon_hoc__ma_mon', 'ma_lop'))

    def get_by_mon_hoc_and_hoc_ky(self, mon_hoc_id: str, hoc_ky_id: str) -> List[LopHocPhan]:
        return list(LopHocPhan.objects.using('neon').filter(
            hoc_phan__mon_hoc_id=mon_hoc_id,
            hoc_phan__id_hoc_ky=hoc_ky_id
        ).select_related(
            'hoc_phan',
            'hoc_phan__mon_hoc',
            'giang_vien',
            'giang_vien__id'
        ).prefetch_related(
            'lichhocdinhky_set',
            'lichhocdinhky_set__phong'
        ).order_by('ma_lop'))

class DangKyHocPhanRepository(IDangKyHocPhanRepository):
    def has_registered_mon_hoc_in_hoc_ky(self, sinh_vien_id: str, mon_hoc_id: str, hoc_ky_id: str) -> bool:
        return DangKyHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            lop_hoc_phan__hoc_phan__mon_hoc_id=mon_hoc_id,
            lop_hoc_phan__hoc_phan__id_hoc_ky=hoc_ky_id,
            trang_thai='da_dang_ky'
        ).exists()

    def is_student_registered(self, sinh_vien_id: str, lop_hoc_phan_id: str) -> bool:
        return DangKyHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            lop_hoc_phan_id=lop_hoc_phan_id,
            trang_thai='da_dang_ky'
        ).exists()

    def find_registered_class_ids(self, sinh_vien_id: str, hoc_ky_id: str) -> List[str]:
        return list(DangKyHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            lop_hoc_phan__hoc_phan__id_hoc_ky=hoc_ky_id,
            trang_thai='da_dang_ky'
        ).values_list('lop_hoc_phan_id', flat=True))

    def find_by_sinh_vien_and_hoc_ky(self, sinh_vien_id: str, hoc_ky_id: str) -> List[DangKyHocPhan]:
        return list(DangKyHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            lop_hoc_phan__hoc_phan__id_hoc_ky=hoc_ky_id,
            trang_thai='da_dang_ky'
        ).select_related(
            'lop_hoc_phan',
            'lop_hoc_phan__hoc_phan',
            'lop_hoc_phan__hoc_phan__mon_hoc',
            'lop_hoc_phan__giang_vien',
            'lop_hoc_phan__giang_vien__id'
        ).prefetch_related(
            'lop_hoc_phan__lichhocdinhky_set',
            'lop_hoc_phan__lichhocdinhky_set__phong'
        ))

    def create(self, data: dict) -> DangKyHocPhan:
        if 'id' not in data:
            data['id'] = uuid.uuid4()
        dang_ky = DangKyHocPhan(**data)
        dang_ky.save(using='neon')
        return dang_ky

    def find_by_sinh_vien_and_lop_hoc_phan(self, sinh_vien_id: str, lop_hoc_phan_id: str) -> Optional[DangKyHocPhan]:
        return DangKyHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            lop_hoc_phan_id=lop_hoc_phan_id
        ).first()

    def update_status(self, id: str, status: str) -> None:
        DangKyHocPhan.objects.using('neon').filter(id=id).update(trang_thai=status)

    def delete(self, id: str) -> None:
        """Delete DangKyHocPhan record - history is tracked in lich_su_dang_ky"""
        DangKyHocPhan.objects.using('neon').filter(id=id).delete()

    def update_lop_hoc_phan(self, id: str, new_lop_hoc_phan_id: str) -> None:
        DangKyHocPhan.objects.using('neon').filter(id=id).update(lop_hoc_phan_id=new_lop_hoc_phan_id)

    def get_registered_classes_by_subject(self, sinh_vien_id: str, mon_hoc_id: str, hoc_ky_id: str) -> List[DangKyHocPhan]:
        return list(DangKyHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            lop_hoc_phan__hoc_phan__mon_hoc_id=mon_hoc_id,
            lop_hoc_phan__hoc_phan__id_hoc_ky=hoc_ky_id,
            trang_thai='da_dang_ky'
        ).select_related('lop_hoc_phan'))

class DangKyTKBRepository(IDangKyTKBRepository):
    def create(self, data: dict) -> DangKyTkb:
        if 'id' not in data:
            data['id'] = uuid.uuid4()
        tkb = DangKyTkb(**data)
        tkb.save(using='neon')
        return tkb

    def delete_by_dang_ky_id(self, dang_ky_id: str) -> None:
        DangKyTkb.objects.using('neon').filter(dang_ky_id=dang_ky_id).delete()

    def update_lop_hoc_phan(self, dang_ky_id: str, new_lop_hoc_phan_id: str) -> None:
        DangKyTkb.objects.using('neon').filter(dang_ky_id=dang_ky_id).update(lop_hoc_phan_id=new_lop_hoc_phan_id)

    def find_registered_lop_hoc_phans_by_hoc_ky(self, sinh_vien_id: str, hoc_ky_id: str) -> List[DangKyTkb]:
        return list(DangKyTkb.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            lop_hoc_phan__hoc_phan__id_hoc_ky=hoc_ky_id
        ).select_related(
            'lop_hoc_phan', 
            'lop_hoc_phan__hoc_phan'
        ).prefetch_related(
            'lop_hoc_phan__lichhocdinhky_set'
        ))

class LichSuDangKyRepository(ILichSuDangKyRepository):
    def upsert_and_log(self, sinh_vien_id: str, hoc_ky_id: str, dang_ky_hoc_phan_id: str, hanh_dong: str) -> None:
        # Find or create LichSuDangKy
        lich_su, created = LichSuDangKy.objects.using('neon').get_or_create(
            sinh_vien_id=sinh_vien_id,
            hoc_ky_id=hoc_ky_id,
            defaults={'id': uuid.uuid4()}
        )
        
        # Create detail log
        ChiTietLichSuDangKy.objects.using('neon').create(
            id=uuid.uuid4(),
            lich_su_dang_ky_id=lich_su.id,
            dang_ky_hoc_phan_id=dang_ky_hoc_phan_id,
            hanh_dong=hanh_dong
        )

    def find_by_sinh_vien_and_hoc_ky(self, sinh_vien_id: str, hoc_ky_id: str) -> Optional[LichSuDangKy]:
        try:
            return LichSuDangKy.objects.using('neon').select_related(
                'hoc_ky'
            ).prefetch_related(
                'chitietlichsudangky_set',
                'chitietlichsudangky_set__dang_ky_hoc_phan',
                'chitietlichsudangky_set__dang_ky_hoc_phan__lop_hoc_phan',
                'chitietlichsudangky_set__dang_ky_hoc_phan__lop_hoc_phan__hoc_phan',
                'chitietlichsudangky_set__dang_ky_hoc_phan__lop_hoc_phan__hoc_phan__mon_hoc'
            ).get(sinh_vien_id=sinh_vien_id, hoc_ky_id=hoc_ky_id)
        except LichSuDangKy.DoesNotExist:
            return None

class LichHocDinhKyRepository(ILichHocDinhKyRepository):
    def find_by_lop_hoc_phan(self, lop_hoc_phan_id: str) -> List[LichHocDinhKy]:
        return list(LichHocDinhKy.objects.using('neon').filter(
            lop_hoc_phan_id=lop_hoc_phan_id
        ).select_related('phong'))

class HocPhiRepository(IHocPhiRepository):
    def get_hoc_phi_by_sinh_vien(self, sinh_vien_id: str, hoc_ky_id: str) -> Optional[HocPhi]:
        try:
            return HocPhi.objects.using('neon').filter(
                sinh_vien_id=sinh_vien_id,
                hoc_ky_id=hoc_ky_id
            ).select_related(
                'chinh_sach',
                'hoc_ky'
            ).prefetch_related(
                'chitiethocphi_set__lop_hoc_phan__hoc_phan__mon_hoc'
            ).first()
        except Exception:
            return None


class TaiLieuRepository:
    def find_by_lop_hoc_phan(self, lop_hoc_phan_id: str) -> List[TaiLieu]:
        return list(TaiLieu.objects.using('neon').filter(
            lop_hoc_phan_id=lop_hoc_phan_id
        ).select_related('uploaded_by').order_by('-created_at'))
