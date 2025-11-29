"""
Infrastructure Layer - Auth Repository Implementation
Implements IAuthRepository interface from Domain
"""
from typing import Optional
from uuid import UUID

from domain.auth.interfaces import IAuthRepository
from infrastructure.persistence.models import TaiKhoan, Users, SinhVien, NganhHoc


class AuthRepository(IAuthRepository):
    """
    Repository implementation for authentication
    Implements domain interface
    """
    
    def find_account_by_username(self, username: str) -> Optional[TaiKhoan]:
        """
        Find account by username
        
        Args:
            username: Login username
            
        Returns:
            TaiKhoan instance or None
        """
        try:
            return TaiKhoan.objects.using('neon').get(ten_dang_nhap=username)
        except TaiKhoan.DoesNotExist:
            return None
    
    def get_user_by_account_id(self, tai_khoan_id: UUID) -> Optional[Users]:
        """
        Get user information by account ID
        
        Args:
            tai_khoan_id: Account UUID
            
        Returns:
            Users instance or None
        """
        try:
            return Users.objects.using('neon').select_related('tai_khoan').get(
                tai_khoan_id=tai_khoan_id
            )
        except Users.DoesNotExist:
            return None
    
    def get_student_info(self, user_id: UUID) -> Optional[dict]:
        """
        Get student-specific information
        
        Args:
            user_id: User UUID
            
        Returns:
            Dictionary with student info or None
        """
        try:
            sinh_vien = SinhVien.objects.using('neon').select_related(
                'nganh', 'nganh__khoa'
            ).get(id=user_id)
            
            return {
                'ma_so_sinh_vien': sinh_vien.ma_so_sinh_vien,
                'lop': sinh_vien.lop,
                'nganh': sinh_vien.nganh.ten_nganh if sinh_vien.nganh else None,
                'khoa': sinh_vien.nganh.khoa.ten_khoa if sinh_vien.nganh and sinh_vien.nganh.khoa else None,
                'khoa_hoc': sinh_vien.khoa_hoc,
            }
        except SinhVien.DoesNotExist:
            return None
