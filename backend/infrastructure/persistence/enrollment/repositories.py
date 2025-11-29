"""
Infrastructure Layer - Enrollment Repository Implementations
"""
from typing import Optional, List, Any
from django.utils import timezone
from application.enrollment.interfaces import (
    IHocKyRepository,
    IKyPhaseRepository,
    IDotDangKyRepository,
    IHocPhanRepository,
    IGhiDanhRepository
)
from infrastructure.persistence.models import (
    HocKy,
    KyPhase,
    DotDangKy,
    HocPhan,
    GhiDanhHocPhan,
    SinhVien
)
import uuid

class HocKyRepository(IHocKyRepository):
    def get_current_hoc_ky(self) -> Optional[HocKy]:
        try:
            return HocKy.objects.using('neon').filter(trang_thai_hien_tai=True).first()
        except Exception:
            return None

class KyPhaseRepository(IKyPhaseRepository):
    def get_current_phase(self, hoc_ky_id: str) -> Optional[KyPhase]:
        try:
            return KyPhase.objects.using('neon').filter(
                hoc_ky_id=hoc_ky_id,
                is_enabled=True
            ).first()
        except Exception:
            return None

class DotDangKyRepository(IDotDangKyRepository):
    def find_toan_truong_by_hoc_ky(self, hoc_ky_id: str, phase: str) -> Optional[DotDangKy]:
        now = timezone.now()
        # Note: phase is not directly in DotDangKy based on legacy logic, 
        # but legacy passed "ghi_danh" as phase. 
        # However, DotDangKy model has `loai_dot`.
        # Legacy logic: findToanTruongByHocKy(hocKyId, phase) 
        # -> where hoc_ky_id = ... and is_check_toan_truong = true and now between start and end
        # The phase argument in legacy seems to map to `loai_dot` or just context.
        # Let's assume `loai_dot` should match or just check time.
        # Legacy: `return this.model.findFirst({ where: { hoc_ky_id, is_check_toan_truong: true, ... } })`
        
        return DotDangKy.objects.using('neon').filter(
            hoc_ky_id=hoc_ky_id,
            is_check_toan_truong=True,
            thoi_gian_bat_dau__lte=now,
            thoi_gian_ket_thuc__gte=now
        ).first()
        
    def is_ghi_danh_for_khoa(self, khoa_id: str, hoc_ky_id: str) -> bool:
        now = timezone.now()
        return DotDangKy.objects.using('neon').filter(
            hoc_ky_id=hoc_ky_id,
            khoa_id=khoa_id,
            thoi_gian_bat_dau__lte=now,
            thoi_gian_ket_thuc__gte=now
        ).exists()

class HocPhanRepository(IHocPhanRepository):
    def find_all_open(self, hoc_ky_id: str) -> List[HocPhan]:
        return list(HocPhan.objects.using('neon').filter(
            id_hoc_ky_id=hoc_ky_id,
            trang_thai_mo=True
        ).select_related(
            'mon_hoc', 
            'mon_hoc__khoa'
        ).prefetch_related(
            'mon_hoc__dexuathocphan_set',
            'mon_hoc__dexuathocphan_set__giang_vien',
            'mon_hoc__dexuathocphan_set__giang_vien__users'
        ))
        
    def find_by_id(self, id: str) -> Optional[HocPhan]:
        try:
            return HocPhan.objects.using('neon').get(id=id)
        except HocPhan.DoesNotExist:
            return None

class GhiDanhRepository(IGhiDanhRepository):
    def is_already_registered(self, sinh_vien_id: str, hoc_phan_id: str) -> bool:
        return GhiDanhHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id,
            hoc_phan_id=hoc_phan_id
        ).exists()
        
    def create(self, data: dict) -> GhiDanhHocPhan:
        # Generate UUID if not provided (Django might handle it but better be safe if model expects it)
        if 'id' not in data:
            data['id'] = uuid.uuid4()
            
        ghi_danh = GhiDanhHocPhan(**data)
        ghi_danh.save(using='neon')
        return ghi_danh
        
    def find_by_sinh_vien(self, sinh_vien_id: str) -> List[GhiDanhHocPhan]:
        return list(GhiDanhHocPhan.objects.using('neon').filter(
            sinh_vien_id=sinh_vien_id
        ).select_related(
            'hoc_phan',
            'hoc_phan__mon_hoc',
            'hoc_phan__mon_hoc__khoa'
        ).prefetch_related(
            'hoc_phan__mon_hoc__dexuathocphan_set',
            'hoc_phan__mon_hoc__dexuathocphan_set__giang_vien',
            'hoc_phan__mon_hoc__dexuathocphan_set__giang_vien__users'
        ))
        
    def delete_many(self, ids: List[str]) -> None:
        GhiDanhHocPhan.objects.using('neon').filter(id__in=ids).delete()
        
    def find_by_ids(self, ids: List[str]) -> List[GhiDanhHocPhan]:
        return list(GhiDanhHocPhan.objects.using('neon').filter(id__in=ids))
