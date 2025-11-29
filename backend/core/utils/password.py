"""
Core Utils - Password Service
Bcrypt password hashing
"""
import bcrypt


class PasswordService:
    """Password hashing and verification using bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash
        
        Args:
            password: Plain text password
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
