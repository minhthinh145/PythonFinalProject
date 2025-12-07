"""
Infrastructure Layer - SinhVien Repository Implementation
"""
from typing import Optional
from domain.sinh_vien.entities import SinhVienEntity
from application.sinh_vien.interfaces import ISinhVienRepository
from infrastructure.persistence.models import SinhVien, Users

class SinhVienRepository(ISinhVienRepository):
    """
    Repository implementation for student
    """
    
    def get_by_id(self, id: str) -> Optional[SinhVienEntity]:
        """
        Get student by ID (User ID - which is also SinhVien.id)
        """
        try:
            # Join with Users, Nganh, Khoa for full details
            sinh_vien = SinhVien.objects.using('neon').select_related(
                'id',  # User (OneToOne)
                'nganh',
                'khoa'
            ).get(id=id)
            
            return self._to_entity(sinh_vien)
        except SinhVien.DoesNotExist:
            return None
            
    def get_by_mssv(self, mssv: str) -> Optional[SinhVienEntity]:
        """
        Get student by MSSV
        """
        try:
            sinh_vien = SinhVien.objects.using('neon').select_related(
                'id',
                'nganh',
                'khoa',
                'nganh__khoa'
            ).get(ma_so_sinh_vien=mssv)
            
            return self._to_entity(sinh_vien)
        except SinhVien.DoesNotExist:
            return None
            
    def _to_entity(self, model: SinhVien) -> SinhVienEntity:
        """
        Convert Django model to Domain Entity
        """
        # Get user info from OneToOne relation (id)
        user = model.id
        
        # Get related names safely
        ten_nganh = model.nganh.ten_nganh if model.nganh else None
        ten_khoa = model.khoa.ten_khoa if model.khoa else None
        
        return SinhVienEntity(
            id=str(model.id.id),  # model.id.id because id is a Users OneToOne
            ma_so_sinh_vien=model.ma_so_sinh_vien,
            ho_ten=user.ho_ten if user else "",
            email=user.email if user else "",
            khoa_id=str(model.khoa_id) if model.khoa_id else None,
            nganh_id=str(model.nganh_id) if model.nganh_id else None,
            lop=model.lop,
            khoa_hoc=model.khoa_hoc,
            ngay_nhap_hoc=model.ngay_nhap_hoc,
            ten_khoa=ten_khoa,
            ten_nganh=ten_nganh,
            trang_thai_hoat_dong=None,
            tai_khoan_id=None
        )
