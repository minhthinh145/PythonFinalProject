"""
Infrastructure Layer - GV LopHocPhan Repository Implementation
"""
from typing import List, Optional
from application.gv.interfaces import (
    IGVLopHocPhanRepository,
    GVLopHocPhanDTO,
    GVLopHocPhanDetailDTO,
    GVStudentDTO,
)
from infrastructure.persistence.models import (
    LopHocPhan,
    GiangVien,
    DangKyHocPhan,
    SinhVien,
    Users,
)


class GVLopHocPhanRepository(IGVLopHocPhanRepository):
    """
    Repository implementation for GV's Lop Hoc Phan operations
    Uses Django ORM with PostgreSQL (Neon)
    """
    
    def get_lop_hoc_phan_by_gv(
        self, 
        gv_user_id: str, 
        hoc_ky_id: Optional[str] = None
    ) -> List[GVLopHocPhanDTO]:
        """
        Get all LopHocPhan assigned to a GiangVien
        """
        # Build queryset with related data
        queryset = LopHocPhan.objects.using('neon').select_related(
            'hoc_phan',
            'hoc_phan__mon_hoc',
            'giang_vien',
        ).filter(
            giang_vien__id=gv_user_id  # GiangVien.id is FK to Users
        )
        
        # Filter by semester if provided
        if hoc_ky_id:
            queryset = queryset.filter(hoc_phan__id_hoc_ky=hoc_ky_id)
        
        # Map to DTOs
        result = []
        for lhp in queryset:
            result.append(self._to_lhp_dto(lhp))
        
        return result
    
    def get_lop_hoc_phan_detail(
        self, 
        lhp_id: str, 
        gv_user_id: str
    ) -> Optional[GVLopHocPhanDetailDTO]:
        """
        Get detail of a LopHocPhan (only if GV is assigned)
        """
        try:
            lhp = LopHocPhan.objects.using('neon').select_related(
                'hoc_phan',
                'hoc_phan__mon_hoc',
            ).get(
                id=lhp_id,
                giang_vien__id=gv_user_id  # Ensure GV owns this LHP
            )
            
            return self._to_lhp_detail_dto(lhp)
            
        except LopHocPhan.DoesNotExist:
            return None
    
    def get_students_of_lhp(
        self, 
        lhp_id: str, 
        gv_user_id: str
    ) -> Optional[List[GVStudentDTO]]:
        """
        Get registered students of a LopHocPhan
        """
        # Get students from DangKyHocPhan with status != 'DA_HUY'
        dang_ky_list = DangKyHocPhan.objects.using('neon').select_related(
            'sinh_vien',
            'sinh_vien__id',  # Users table
        ).filter(
            lop_hoc_phan__id=lhp_id,
            trang_thai__in=['DANG_KY', 'DA_DUYET']  # Active registrations
        )
        
        result = []
        for dk in dang_ky_list:
            sv = dk.sinh_vien
            user = sv.id  # OneToOne to Users
            
            result.append(GVStudentDTO(
                id=str(sv.id.id),  # Users.id is UUID
                mssv=sv.ma_so_sinh_vien,
                hoTen=user.ho_ten,
                lop=sv.lop,
                email=user.email,
            ))
        
        return result
    
    def verify_gv_owns_lhp(self, lhp_id: str, gv_user_id: str) -> bool:
        """
        Check if GV is assigned to the LopHocPhan
        """
        return LopHocPhan.objects.using('neon').filter(
            id=lhp_id,
            giang_vien__id=gv_user_id
        ).exists()
    
    def _to_lhp_dto(self, lhp: LopHocPhan) -> GVLopHocPhanDTO:
        """Convert Django model to DTO"""
        hoc_phan = lhp.hoc_phan
        mon_hoc = hoc_phan.mon_hoc if hoc_phan else None
        
        return GVLopHocPhanDTO(
            id=str(lhp.id),
            ma_lop=lhp.ma_lop,
            so_luong_hien_tai=lhp.so_luong_hien_tai,
            so_luong_toi_da=lhp.so_luong_toi_da,
            hoc_phan={
                "ten_hoc_phan": hoc_phan.ten_hoc_phan if hoc_phan else None,
                "mon_hoc": {
                    "ma_mon": mon_hoc.ma_mon if mon_hoc else None,
                    "ten_mon": mon_hoc.ten_mon if mon_hoc else None,
                    "so_tin_chi": mon_hoc.so_tin_chi if mon_hoc else None,
                } if mon_hoc else {}
            }
        )
    
    def _to_lhp_detail_dto(self, lhp: LopHocPhan) -> GVLopHocPhanDetailDTO:
        """Convert Django model to Detail DTO"""
        hoc_phan = lhp.hoc_phan
        mon_hoc = hoc_phan.mon_hoc if hoc_phan else None
        
        return GVLopHocPhanDetailDTO(
            id=str(lhp.id),
            ma_lop=lhp.ma_lop,
            hoc_phan={
                "ten_hoc_phan": hoc_phan.ten_hoc_phan if hoc_phan else None,
                "mon_hoc": {
                    "ma_mon": mon_hoc.ma_mon if mon_hoc else None,
                    "ten_mon": mon_hoc.ten_mon if mon_hoc else None,
                    "so_tin_chi": mon_hoc.so_tin_chi if mon_hoc else None,
                } if mon_hoc else {}
            }
        )
