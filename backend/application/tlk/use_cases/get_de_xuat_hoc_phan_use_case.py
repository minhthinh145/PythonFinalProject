"""
Application Layer - TLK Get De Xuat Hoc Phan Use Case
"""
from core.types.service_result import ServiceResult
from application.tlk.interfaces import ITLKRepository, ITLKDeXuatRepository


class GetDeXuatHocPhanUseCase:
    """
    Use case for TLK to view their De Xuat Hoc Phan list
    """
    
    def __init__(
        self, 
        tlk_repo: ITLKRepository,
        de_xuat_repo: ITLKDeXuatRepository
    ):
        self.tlk_repo = tlk_repo
        self.de_xuat_repo = de_xuat_repo
    
    def execute(self, user_id: str, hoc_ky_id: str = None) -> ServiceResult:
        """
        Execute the use case
        
        Args:
            user_id: ID of TLK user
            hoc_ky_id: Optional filter by hoc_ky
        """
        # 1. Get khoa_id from TLK user
        khoa_id = self.tlk_repo.get_khoa_id_by_user(user_id)
        if not khoa_id:
            return ServiceResult.fail("Không tìm thấy thông tin khoa của trợ lý khoa")
        
        # 2. Get de xuat list
        de_xuats = self.de_xuat_repo.get_de_xuat_by_khoa(khoa_id, hoc_ky_id)
        
        # 3. Convert to response format
        data = [
            {
                'id': dx.id,
                'maHocPhan': dx.ma_hoc_phan,
                'tenHocPhan': dx.ten_hoc_phan,
                'soTinChi': dx.so_tin_chi,
                'giangVien': dx.giang_vien,
                'trangThai': dx.trang_thai,
            }
            for dx in de_xuats
        ]
        
        return ServiceResult.ok(
            message=f"Đã tải {len(data)} đề xuất học phần",
            data=data
        )
