"""
Domain Layer - Auth Repository Interface
Dependency Inversion: Domain defines interface, Infrastructure implements
"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from infrastructure.persistence.models import TaiKhoan, Users


class IAuthRepository(ABC):
    """Repository interface for authentication"""
    
    @abstractmethod
    def find_account_by_username(self, username: str) -> Optional[TaiKhoan]:
        """
        Find account by username
        
        Args:
            username: Login username
            
        Returns:
            TaiKhoan instance or None
        """
        pass
    
    @abstractmethod
    def get_user_by_account_id(self, tai_khoan_id: UUID) -> Optional[Users]:
        """
        Get user information by account ID
        
        Args:
            tai_khoan_id: Account UUID
            
        Returns:
            Users instance or None
        """
        pass
    
    @abstractmethod
    def get_student_info(self, user_id: UUID) -> Optional[dict]:
        """
        Get student-specific information
        
        Args:
            user_id: User UUID
            
        Returns:
            Dictionary with student info or None
        """
        pass
