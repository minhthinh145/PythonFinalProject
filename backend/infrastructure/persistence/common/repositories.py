"""
Infrastructure Layer - Common Repositories

Concrete implementations of common repository interfaces
"""
from typing import Optional, List, Any
from infrastructure.persistence.models import HocKy, NienKhoa, NganhHoc as Nganh
from application.common.interfaces import IHocKyRepository, INienKhoaRepository, INganhRepository


class HocKyRepository(IHocKyRepository):
    """Repository for HocKy (Semester) operations"""
    
    def find_hien_hanh(self) -> Optional[HocKy]:
        """Find the current active semester"""
        return HocKy.objects.using('neon').filter(
            trang_thai_hien_tai=True
        ).select_related('id_nien_khoa').first()
    
    def find_by_id(self, id: str) -> Optional[HocKy]:
        """Find semester by ID"""
        return HocKy.objects.using('neon').filter(
            id=id
        ).select_related('id_nien_khoa').first()
    
    def get_all(self) -> List[HocKy]:
        """Get all semesters with nien khoa, ordered by time"""
        return list(HocKy.objects.using('neon').select_related(
            'id_nien_khoa'
        ).order_by(
            '-id_nien_khoa__nam_hoc_bat_dau',
            '-id_nien_khoa__nam_hoc_bat_dau',
            '-ngay_bat_dau'
        ))

    def set_current_semester(self, hoc_ky_id: str) -> None:
        """Set the current active semester"""
        # 1. Set all to False
        HocKy.objects.using('neon').update(trang_thai_hien_tai=False)
        
        # 2. Set target to True
        HocKy.objects.using('neon').filter(id=hoc_ky_id).update(trang_thai_hien_tai=True)

    def update_dates(self, id: str, start_at: Any, end_at: Any) -> None:
        """Update semester start and end dates"""
        HocKy.objects.using('neon').filter(id=id).update(
            ngay_bat_dau=start_at,
            ngay_ket_thuc=end_at
        )


class NienKhoaRepository(INienKhoaRepository):
    """Repository for NienKhoa (Academic Year) operations"""
    
    def find_by_id(self, id: str) -> Optional[NienKhoa]:
        """Find academic year by ID"""
        return NienKhoa.objects.using('neon').filter(id=id).first()


class NganhRepository(INganhRepository):
    """Repository for Nganh (Program/Major) operations"""
    
    def find_all(self, khoa_id: Optional[str] = None) -> List[Nganh]:
        """Find all programs, optionally filtered by faculty"""
        query = Nganh.objects.using('neon').select_related('khoa')
        
        if khoa_id:
            query = query.filter(khoa_id=khoa_id)
        
        return list(query.order_by('ten_nganh'))
    
    def find_without_policy(self, hoc_ky_id: str, khoa_id: str) -> List[Nganh]:
        """
        Find programs without tuition policy for given semester and faculty
        
        Note: This requires checking ChinhSachTinChi table
        Will implement when ChinhSachTinChi module is ported
        """
        # TODO: Add subquery to exclude programs with existing policy
        from infrastructure.persistence.models import ChinhSachTinChi
        
        # Get all programs in the faculty
        all_nganh = Nganh.objects.using('neon').filter(khoa_id=khoa_id)
        
        # Get programs with existing policy
        nganh_with_policy = ChinhSachTinChi.objects.using('neon').filter(
            hoc_ky_id=hoc_ky_id,
            nganh__khoa_id=khoa_id
        ).values_list('nganh_id', flat=True)
        
        # Exclude programs with policy
        return list(all_nganh.exclude(
            id__in=nganh_with_policy
        ).select_related('khoa').order_by('ten_nganh'))
