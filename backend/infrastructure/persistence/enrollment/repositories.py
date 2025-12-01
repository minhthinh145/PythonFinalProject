"""
Infrastructure Layer - Enrollment Repository Implementations
"""
from typing import Optional, List, Any
from django.utils import timezone
from datetime import datetime
from application.enrollment.interfaces import (
    IHocKyRepository, IKyPhaseRepository, IDotDangKyRepository,
    IHocPhanRepository, IGhiDanhRepository, IHocPhiRepository, IKhoaRepository
)
from infrastructure.persistence.models import (
    HocKy, KyPhase, DotDangKy, HocPhan, LopHocPhan, HocPhi, Khoa,
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

    def get_all_hoc_ky(self) -> List[HocKy]:
        return list(HocKy.objects.using('neon').select_related('id_nien_khoa').all().order_by('-ngay_bat_dau'))

    def update_dates(self, id: str, start_at: Any, end_at: Any) -> None:
        HocKy.objects.using('neon').filter(id=id).update(
            ngay_bat_dau=start_at,
            ngay_ket_thuc=end_at
        )

class KyPhaseRepository(IKyPhaseRepository):
    def get_current_phase(self, hoc_ky_id: str) -> Optional[KyPhase]:
        try:
            return KyPhase.objects.using('neon').filter(
                hoc_ky_id=hoc_ky_id,
                is_enabled=True
            ).first()
        except Exception:
            return None

    def create_bulk(self, phases: List[dict], hoc_ky_id: str) -> List[dict]:
        # 1. Delete existing phases for this semester
        # KyPhase.objects.using('neon').filter(hoc_ky_id=hoc_ky_id).delete()
        
        # 2. Create new phases
        new_phases = []
        result_data = []
        for p in phases:
            # Parse dates
            start_at = datetime.strptime(p.get('ngayBatDau'), '%Y-%m-%d') if p.get('ngayBatDau') else None
            end_at = datetime.strptime(p.get('ngayKetThuc'), '%Y-%m-%d') if p.get('ngayKetThuc') else None

            phase = KyPhase.objects.using('neon').create(
                id=uuid.uuid4(),
                hoc_ky_id=hoc_ky_id,
                phase=p.get('tenPhase'),
                start_at=start_at,
                end_at=end_at,
                is_enabled=True # Default to enabled
            )
            # phase.save(using='neon')
            new_phases.append(phase)
            
            result_data.append({
                "id": str(uuid.uuid4()),
                "hocKyId": str(hoc_ky_id),
                "tenPhase": p.get('tenPhase'),
                "ngayBatDau": p.get('ngayBatDau'),
                "ngayKetThuc": p.get('ngayKetThuc'),
                "isEnabled": True
            })
            
        # KyPhase.objects.using('neon').bulk_create(new_phases)
        
        return result_data

    def find_by_hoc_ky(self, hoc_ky_id: str) -> List[KyPhase]:
        return list(KyPhase.objects.using('neon').filter(hoc_ky_id=hoc_ky_id))

class DotDangKyRepository(IDotDangKyRepository):
    def find_toan_truong_by_hoc_ky(self, hoc_ky_id: str, phase: str) -> Optional[DotDangKy]:
        now = timezone.now()

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

    def find_active_dot_dang_ky(self, hoc_ky_id: str) -> Optional[DotDangKy]:
        now = timezone.now()
        return DotDangKy.objects.using('neon').filter(
            hoc_ky_id=hoc_ky_id,
            thoi_gian_bat_dau__lte=now,
            thoi_gian_ket_thuc__gte=now
        ).first()

    def delete_by_hoc_ky(self, hoc_ky_id: str) -> None:
        DotDangKy.objects.using('neon').filter(hoc_ky_id=hoc_ky_id).delete()

    def create(self, data: dict) -> DotDangKy:
        if 'id' not in data:
            data['id'] = uuid.uuid4()
        
        dot = DotDangKy(**data)
        dot.save(using='neon')
        return dot

    def find_by_hoc_ky_and_loai(self, hoc_ky_id: str, loai_dot: str) -> List[DotDangKy]:
        return list(DotDangKy.objects.using('neon').filter(
            hoc_ky_id=hoc_ky_id,
            loai_dot=loai_dot
        ).order_by('thoi_gian_bat_dau'))

    def update(self, id: str, data: dict) -> Optional[DotDangKy]:
        try:
            dot = DotDangKy.objects.using('neon').get(id=id)
            for key, value in data.items():
                setattr(dot, key, value)
            dot.save(using='neon')
            return dot
        except DotDangKy.DoesNotExist:
            return None

class HocPhanRepository(IHocPhanRepository):
    def find_all_open(self, hoc_ky_id: str) -> List[HocPhan]:
        return list(HocPhan.objects.using('neon').filter(
            id_hoc_ky_id=hoc_ky_id,
            trang_thai_mo=True
        ).select_related(
            'mon_hoc', 
            'mon_hoc__khoa'
        ))
        
    def find_by_id(self, id: str) -> Optional[HocPhan]:
        try:
            return HocPhan.objects.using('neon').get(id=id)
        except HocPhan.DoesNotExist:
            return None

    def find_lop_hoc_phan_by_hoc_ky(self, hoc_ky_id: str) -> List[LopHocPhan]:
        """
        Get all LopHocPhan for a semester with related data
        Used by TraCuuHocPhan to show class listings
        """
        return list(LopHocPhan.objects.using('neon').filter(
            hoc_phan__id_hoc_ky_id=hoc_ky_id
        ).select_related(
            'hoc_phan',
            'hoc_phan__mon_hoc',
            'giang_vien',
            'giang_vien__id',  # Users via OneToOne
        ).prefetch_related(
            'lichhocdinhky_set',
            'lichhocdinhky_set__phong',
            'dangkyhocphan_set'
        ))



class KhoaRepository(IKhoaRepository):
    def get_all(self) -> List[Any]:
        return list(Khoa.objects.using('neon').all())

class HocPhiRepository(IHocPhiRepository):
    def get_hoc_phi_by_sinh_vien(self, sinh_vien_id: str, hoc_ky_id: str) -> Optional[Any]:
        # Simple query without prefetch_related to avoid complexity
        try:
            return HocPhi.objects.using('neon').get(sinh_vien_id=sinh_vien_id, hoc_ky_id=hoc_ky_id)
        except HocPhi.DoesNotExist:
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
            'hoc_phan__mon_hoc__dexuathocphan_set__giang_vien_de_xuat'
        ))
        
    def delete_many(self, ids: List[str]) -> None:
        GhiDanhHocPhan.objects.using('neon').filter(id__in=ids).delete()
        
    def find_by_ids(self, ids: List[str]) -> List[GhiDanhHocPhan]:
        return list(GhiDanhHocPhan.objects.using('neon').filter(id__in=ids))
