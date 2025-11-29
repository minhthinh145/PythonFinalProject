
from typing import TypeVar, Generic, Optional
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class ServiceResult(Generic[T]):
   
    success: bool
    message: str
    data: Optional[T] = None
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    
    @staticmethod
    def ok(data: T, message: str = "Success") -> 'ServiceResult[T]':
        """Success result"""
        return ServiceResult(success=True, message=message, data=data, status_code=200)
    
    @staticmethod
    def fail(message: str, status_code: int = 400, error_code: Optional[str] = None) -> 'ServiceResult':
        """Failure result"""
        return ServiceResult(success=False, message=message, data=None, status_code=status_code, error_code=error_code)
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> 'ServiceResult':
        """401 Unauthorized"""
        return ServiceResult(success=False, message=message, data=None, status_code=401)
    
    @staticmethod
    def forbidden(message: str = "Forbidden") -> 'ServiceResult':
        """403 Forbidden"""
        return ServiceResult(success=False, message=message, data=None, status_code=403)
    
    @staticmethod
    def not_found(message: str = "Not Found") -> 'ServiceResult':
        """404 Not Found"""
        return ServiceResult(success=False, message=message, data=None, status_code=404)
