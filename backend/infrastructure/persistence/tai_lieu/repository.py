"""
Infrastructure Layer - TaiLieu Repository Implementation

Implements ITaiLieuRepository using Django ORM.
"""
from typing import List, Optional
from datetime import datetime
import uuid

from application.tai_lieu.interfaces.repositories import (
    ITaiLieuRepository,
    TaiLieuDTO,
    CreateTaiLieuDTO,
)
from infrastructure.persistence.models import (
    TaiLieu,
    LopHocPhan,
    DangKyHocPhan,
    SinhVien,
)


class TaiLieuRepository(ITaiLieuRepository):
    """
    TaiLieu repository implementation using Django ORM
    """
    
    def find_by_lop_hoc_phan(self, lop_hoc_phan_id: str) -> List[TaiLieuDTO]:
        """Get all TaiLieu for a LopHocPhan"""
        documents = TaiLieu.objects.using('neon').filter(
            lop_hoc_phan_id=lop_hoc_phan_id
        ).select_related('uploaded_by').order_by('-created_at')
        
        result = []
        for doc in documents:
            result.append(TaiLieuDTO(
                id=str(doc.id),
                ten_tai_lieu=doc.ten_tai_lieu,
                file_path=doc.file_path,
                file_type=doc.file_type or '',
                created_at=doc.created_at.isoformat() if doc.created_at else None,
                uploaded_by_id=str(doc.uploaded_by_id) if doc.uploaded_by_id else None,
                uploaded_by_name=doc.uploaded_by.ho_ten if doc.uploaded_by else None,
            ))
        
        return result
    
    def find_by_id(self, tai_lieu_id: str) -> Optional[TaiLieuDTO]:
        """Get TaiLieu by ID"""
        try:
            doc = TaiLieu.objects.using('neon').select_related(
                'uploaded_by'
            ).get(id=tai_lieu_id)
            
            return TaiLieuDTO(
                id=str(doc.id),
                ten_tai_lieu=doc.ten_tai_lieu,
                file_path=doc.file_path,
                file_type=doc.file_type or '',
                created_at=doc.created_at.isoformat() if doc.created_at else None,
                uploaded_by_id=str(doc.uploaded_by_id) if doc.uploaded_by_id else None,
                uploaded_by_name=doc.uploaded_by.ho_ten if doc.uploaded_by else None,
            )
        except TaiLieu.DoesNotExist:
            return None
    
    def create(self, data: CreateTaiLieuDTO) -> TaiLieuDTO:
        """Create a new TaiLieu record"""
        doc = TaiLieu.objects.using('neon').create(
            id=uuid.uuid4(),
            lop_hoc_phan_id=data.lop_hoc_phan_id,
            ten_tai_lieu=data.ten_tai_lieu,
            file_path=data.file_path,
            file_type=data.file_type,
            uploaded_by_id=data.uploaded_by,
            created_at=datetime.now()
        )
        
        return TaiLieuDTO(
            id=str(doc.id),
            ten_tai_lieu=doc.ten_tai_lieu,
            file_path=doc.file_path,
            file_type=doc.file_type or '',
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            uploaded_by_id=str(doc.uploaded_by_id) if doc.uploaded_by_id else None,
            uploaded_by_name=None,  # Not loaded in create
        )
    
    def delete(self, tai_lieu_id: str) -> bool:
        """Delete TaiLieu by ID"""
        try:
            deleted, _ = TaiLieu.objects.using('neon').filter(id=tai_lieu_id).delete()
            return deleted > 0
        except Exception:
            return False
    
    def update_name(self, tai_lieu_id: str, new_name: str) -> Optional[TaiLieuDTO]:
        """Update TaiLieu name"""
        try:
            doc = TaiLieu.objects.using('neon').get(id=tai_lieu_id)
            doc.ten_tai_lieu = new_name
            doc.save(using='neon')
            
            return TaiLieuDTO(
                id=str(doc.id),
                ten_tai_lieu=doc.ten_tai_lieu,
                file_path=doc.file_path,
                file_type=doc.file_type or '',
                created_at=doc.created_at.isoformat() if doc.created_at else None,
                uploaded_by_id=str(doc.uploaded_by_id) if doc.uploaded_by_id else None,
                uploaded_by_name=None,
            )
        except TaiLieu.DoesNotExist:
            return None
    
    def get_lop_hoc_phan_owner(self, lop_hoc_phan_id: str) -> Optional[str]:
        """Get the GiangVien user_id who owns this LopHocPhan"""
        try:
            lhp = LopHocPhan.objects.using('neon').get(id=lop_hoc_phan_id)
            return str(lhp.giang_vien_id) if lhp.giang_vien_id else None
        except LopHocPhan.DoesNotExist:
            return None
    
    def is_student_enrolled(self, lop_hoc_phan_id: str, sinh_vien_user_id: str) -> bool:
        """Check if a SinhVien is enrolled in a LopHocPhan"""
        try:
            # SinhVien.id is a OneToOne FK to Users.id, so we can filter directly
            print(f"[DEBUG] is_student_enrolled: lhp_id={lop_hoc_phan_id}, user_id={sinh_vien_user_id}")
            sinh_vien = SinhVien.objects.using('neon').filter(
                id=sinh_vien_user_id
            ).first()
            
            print(f"[DEBUG] sinh_vien found: {sinh_vien is not None}")
            if not sinh_vien:
                return False
            
            # Use sinh_vien.pk to get the actual UUID (sinh_vien.id returns the Users object!)
            sinh_vien_pk = sinh_vien.pk
            print(f"[DEBUG] sinh_vien.pk={sinh_vien_pk}")
            
            # Check enrollment
            exists = DangKyHocPhan.objects.using('neon').filter(
                sinh_vien_id=sinh_vien_pk,
                lop_hoc_phan_id=lop_hoc_phan_id,
                trang_thai__in=['da_dang_ky', 'da_duyet', 'cho_thanh_toan', 'da_thanh_toan', 'completed']
            ).exists()
            print(f"[DEBUG] enrollment exists: {exists}")
            return exists
        except Exception as e:
            print(f"[DEBUG] Exception in is_student_enrolled: {e}")
            return False
