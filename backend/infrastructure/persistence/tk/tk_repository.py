"""
Infrastructure Layer - TK (Truong Khoa) Repository Implementation
"""
from typing import List, Optional
from datetime import datetime, timezone

from application.tk.interfaces import (
    ITruongKhoaRepository,
    IDeXuatHocPhanRepository,
    DeXuatHocPhanForTKDTO,
)
from infrastructure.persistence.models import (
    TruongKhoa,
    DeXuatHocPhan,
    DeXuatHocPhanLog,
    Users,
    MonHoc,
    GiangVien,
    HocKy,
)


class TKTruongKhoaRepository(ITruongKhoaRepository):
    """
    Repository implementation for TruongKhoa
    """
    
    def find_by_user_id(self, user_id: str) -> Optional[dict]:
        """
        Find TruongKhoa by user_id
        Returns dict with id and khoa_id
        """
        try:
            tk = TruongKhoa.objects.using('neon').select_related('khoa').get(id=user_id)
            return {
                'id': str(tk.id.id),  # User ID from OneToOneField
                'khoa_id': str(tk.khoa_id),
            }
        except TruongKhoa.DoesNotExist:
            return None
    
    def get_khoa_id(self, user_id: str) -> Optional[str]:
        """
        Get khoa_id for truong khoa
        """
        result = self.find_by_user_id(user_id)
        return result['khoa_id'] if result else None


class TKDeXuatHocPhanRepository(IDeXuatHocPhanRepository):
    """
    Repository implementation for DeXuatHocPhan operations by TK
    """
    
    def find_by_khoa_and_status(self, khoa_id: str, trang_thai: str) -> List[DeXuatHocPhanForTKDTO]:
        """
        Find all DeXuatHocPhan for a khoa with specific status
        """
        de_xuats = DeXuatHocPhan.objects.using('neon').select_related(
            'mon_hoc', 'giang_vien_de_xuat', 'giang_vien_de_xuat__id'
        ).filter(
            khoa_id=khoa_id,
            trang_thai=trang_thai
        ).order_by('-created_at')
        
        results = []
        for dx in de_xuats:
            # Get giang vien name
            giang_vien_name = ""
            if dx.giang_vien_de_xuat:
                try:
                    giang_vien_name = dx.giang_vien_de_xuat.id.ho_ten
                except:
                    pass
            
            results.append(DeXuatHocPhanForTKDTO(
                id=str(dx.id),
                ma_hoc_phan=dx.mon_hoc.ma_mon if dx.mon_hoc else "",
                ten_hoc_phan=dx.mon_hoc.ten_mon if dx.mon_hoc else "",
                so_tin_chi=dx.mon_hoc.so_tin_chi if dx.mon_hoc else 0,
                giang_vien=giang_vien_name,
                trang_thai=dx.trang_thai or "",
            ))
        
        return results
    
    def find_by_id(self, de_xuat_id: str) -> Optional[dict]:
        """
        Find DeXuatHocPhan by ID
        Returns dict with id, khoa_id, trang_thai
        """
        try:
            dx = DeXuatHocPhan.objects.using('neon').get(id=de_xuat_id)
            return {
                'id': str(dx.id),
                'khoa_id': str(dx.khoa_id),
                'trang_thai': dx.trang_thai,
            }
        except DeXuatHocPhan.DoesNotExist:
            return None
    
    def update_trang_thai(self, de_xuat_id: str, trang_thai: str, nguoi_duyet_id: str) -> bool:
        """
        Update trang_thai for DeXuatHocPhan (duyet)
        Also creates a log entry
        After TK approves, cap_duyet moves to 'pdt' (Phong Dao Tao)
        """
        try:
            dx = DeXuatHocPhan.objects.using('neon').get(id=de_xuat_id)
            old_trang_thai = dx.trang_thai
            dx.trang_thai = trang_thai
            dx.cap_duyet_hien_tai = 'pdt'  # Move to next approval level
            dx.updated_at = datetime.now(timezone.utc)
            dx.save(using='neon')
            
            # Create log entry
            import uuid
            DeXuatHocPhanLog.objects.using('neon').create(
                id=uuid.uuid4(),
                de_xuat_id=de_xuat_id,
                thoi_gian=datetime.now(timezone.utc),
                hanh_dong='duyet_tk',
                nguoi_thuc_hien_id=nguoi_duyet_id,
                ghi_chu=f'Trưởng khoa duyệt. Trạng thái: {old_trang_thai} -> {trang_thai}'
            )
            
            return True
        except Exception as e:
            print(f"Error updating trang_thai: {e}")
            return False
    
    def reject(self, de_xuat_id: str, nguoi_tu_choi_id: str) -> bool:
        """
        Reject DeXuatHocPhan
        """
        try:
            dx = DeXuatHocPhan.objects.using('neon').get(id=de_xuat_id)
            old_trang_thai = dx.trang_thai
            dx.trang_thai = 'tu_choi'
            dx.cap_duyet_hien_tai = 'truong_khoa'
            dx.updated_at = datetime.now(timezone.utc)
            dx.save(using='neon')
            
            # Create log entry
            import uuid
            DeXuatHocPhanLog.objects.using('neon').create(
                id=uuid.uuid4(),
                de_xuat_id=de_xuat_id,
                thoi_gian=datetime.now(timezone.utc),
                hanh_dong='tu_choi_tk',
                nguoi_thuc_hien_id=nguoi_tu_choi_id,
                ghi_chu=f'Trưởng khoa từ chối'
            )
            
            return True
        except Exception as e:
            print(f"Error rejecting de_xuat: {e}")
            return False
