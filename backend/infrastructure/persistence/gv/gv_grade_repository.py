"""
Infrastructure Layer - GV Grade Repository Implementation
"""
from typing import List, Dict, Any
from django.db import transaction
import uuid
from application.gv.interfaces import (
    IGVGradeRepository,
    GVGradeDTO,
)
from infrastructure.persistence.models import (
    KetQuaHocPhan,
    DangKyHocPhan,
    LopHocPhan,
)


class GVGradeRepository(IGVGradeRepository):
    """
    Repository implementation for GV's grade operations
    Uses Django ORM with PostgreSQL (Neon)
    """
    
    def get_grades(self, lhp_id: str) -> List[GVGradeDTO]:
        """
        Get all grades for a LopHocPhan
        """
        grades = KetQuaHocPhan.objects.using('neon').filter(
            lop_hoc_phan__id=lhp_id
        )
        
        result = []
        for grade in grades:
            result.append(GVGradeDTO(
                sinh_vien_id=str(grade.sinh_vien_id),
                diem_so=float(grade.diem_so) if grade.diem_so is not None else None,
            ))
        
        return result
    
    def upsert_grades(
        self, 
        lhp_id: str, 
        grades: List[Dict[str, Any]]
    ) -> bool:
        """
        Insert or update grades for students
        """
        try:
            # Get LopHocPhan to fetch related info
            lhp = LopHocPhan.objects.using('neon').select_related(
                'hoc_phan',
                'hoc_phan__mon_hoc',
                'hoc_phan__id_hoc_ky',
            ).get(id=lhp_id)
            
            mon_hoc_id = lhp.hoc_phan.mon_hoc_id
            hoc_ky_id = lhp.hoc_phan.id_hoc_ky_id
            
            with transaction.atomic(using='neon'):
                for grade_data in grades:
                    sinh_vien_id = grade_data['sinh_vien_id']
                    diem_so = grade_data['diem_so']
                    
                    # Determine status based on grade (>= 4.0 is passing)
                    status = 'dat' if (diem_so is not None and diem_so >= 4.0) else 'khong_dat'
                    
                    # Upsert using get_or_create + update
                    ket_qua, created = KetQuaHocPhan.objects.using('neon').get_or_create(
                        sinh_vien_id=sinh_vien_id,
                        mon_hoc_id=mon_hoc_id,
                        hoc_ky_id=hoc_ky_id,
                        defaults={
                            'id': uuid.uuid4(),
                            'lop_hoc_phan_id': lhp_id,
                            'diem_so': diem_so,
                            'trang_thai': status,
                        }
                    )
                    
                    if not created:
                        # Update existing record
                        ket_qua.diem_so = diem_so
                        ket_qua.lop_hoc_phan_id = lhp_id
                        ket_qua.save(using='neon')
            
            return True
            
        except Exception as e:
            import traceback
            print(f"Error upserting grades: {e}")
            traceback.print_exc()
            return False
    
    def validate_students_in_lhp(
        self, 
        lhp_id: str, 
        sinh_vien_ids: List[str]
    ) -> bool:
        """
        Validate that all sinh_vien_ids are registered in the LHP
        """
        # Get count of registered students with matching IDs
        registered_count = DangKyHocPhan.objects.using('neon').filter(
            lop_hoc_phan__id=lhp_id,
            sinh_vien__id__id__in=sinh_vien_ids,  # SinhVien.id is FK to Users.id
            trang_thai__in=['da_dang_ky', 'dang_ky', 'da_duyet']
        ).count()
        
        return registered_count == len(sinh_vien_ids)
