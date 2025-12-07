"""
Core Utils - Password Service
Compatible with Django password hashing (pbkdf2_sha256)
"""
from django.contrib.auth.hashers import check_password, make_password


class PasswordService:
    """Password hashing and verification using Django's built-in hashers"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using Django's make_password (pbkdf2_sha256)
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return make_password(password)
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash using Django's check_password
        
        Args:
            password: Plain text password
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return check_password(password, hashed_password)
        except Exception:
            return False

