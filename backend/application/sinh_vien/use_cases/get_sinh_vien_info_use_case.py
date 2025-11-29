"""
Application Layer - Get SinhVien Info Use Case
"""
from core.types import ServiceResult
from application.sinh_vien.interfaces import ISinhVienRepository
from application.sinh_vien.dtos.get_sinh_vien_info_dto import GetSinhVienInfoResponseDTO

class GetSinhVienInfoUseCase:
    """
    Use case to get student information
    """
    
    def __init__(self, sinh_vien_repository: ISinhVienRepository):
        self.sinh_vien_repository = sinh_vien_repository
        
    def execute(self, user_id: str) -> ServiceResult:
        """
        Execute get info logic
        
        Args:
            user_id: ID of the user (student)
            
        Returns:
            ServiceResult with student info
        """
        sinh_vien = self.sinh_vien_repository.get_by_id(user_id)
        
        if not sinh_vien:
            return ServiceResult.not_found("Không tìm thấy thông tin sinh viên")
            
        # Map entity to DTO
        dto = GetSinhVienInfoResponseDTO(
            id=sinh_vien.id,
            maSoSinhVien=sinh_vien.ma_so_sinh_vien,
            hoTen=sinh_vien.ho_ten,
            khoaId=sinh_vien.khoa_id,
            nganhId=sinh_vien.nganh_id,
            lop=sinh_vien.lop,
            khoaHoc=sinh_vien.khoa_hoc,
            ngayNhapHoc=sinh_vien.ngay_nhap_hoc.isoformat() if sinh_vien.ngay_nhap_hoc else None,
            tenKhoa=sinh_vien.ten_khoa,
            tenNganh=sinh_vien.ten_nganh,
            email=sinh_vien.email
        )
        
        return ServiceResult.ok(dto.__dict__)
