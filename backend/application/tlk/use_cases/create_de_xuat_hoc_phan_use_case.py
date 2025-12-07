"""
Application Layer - TLK Create De Xuat Hoc Phan Use Case
"""
from typing import Optional
from dataclasses import dataclass
from core.types.service_result import ServiceResult
from application.tlk.interfaces import ITLKRepository, ITLKDeXuatRepository


@dataclass
class CreateDeXuatHocPhanRequest:
    """Request DTO for creating de xuat"""
    ma_hoc_phan: str  # Actually mon_hoc_id
    ma_giang_vien: str  # giang_vien_id


class CreateDeXuatHocPhanUseCase:
    """
    Use case for TLK to create De Xuat Hoc Phan
    
    Business Rules:
    - TLK can only create de xuat for their khoa
    - Must specify mon_hoc and optionally giang_vien
    - Creates with status 'cho_duyet' and cap_duyet 'truong_khoa'
    """
    
    def __init__(
        self, 
        tlk_repo: ITLKRepository,
        de_xuat_repo: ITLKDeXuatRepository,
        hoc_ky_repo=None
    ):
        self.tlk_repo = tlk_repo
        self.de_xuat_repo = de_xuat_repo
        self.hoc_ky_repo = hoc_ky_repo
    
    def execute(
        self,
        user_id: str,
        request: CreateDeXuatHocPhanRequest,
        hoc_ky_id: Optional[str] = None
    ) -> ServiceResult:
        """
        Execute the use case
        
        Args:
            user_id: ID of TLK user
            request: CreateDeXuatHocPhanRequest
            hoc_ky_id: Optional hoc_ky_id (uses current if not provided)
        """
        # 1. Get khoa_id from TLK user
        khoa_id = self.tlk_repo.get_khoa_id_by_user(user_id)
        if not khoa_id:
            return ServiceResult.fail("Không tìm thấy thông tin khoa của trợ lý khoa")
        
        # 2. Get hoc_ky_id if not provided
        if not hoc_ky_id:
            from infrastructure.persistence.tlk.tlk_repository import TLKThoiKhoaBieuRepository
            tkb_repo = TLKThoiKhoaBieuRepository()
            hoc_ky_id = tkb_repo.get_hoc_ky_hien_hanh()
            
            if not hoc_ky_id:
                return ServiceResult.fail("Không tìm thấy học kỳ hiện hành")
        
        # 3. Validate mon_hoc belongs to khoa
        # (For now, we trust frontend sends valid mon_hoc_id)
        
        # 4. Create de xuat
        success = self.de_xuat_repo.create_de_xuat(
            khoa_id=khoa_id,
            nguoi_tao_id=user_id,
            hoc_ky_id=hoc_ky_id,
            mon_hoc_id=request.ma_hoc_phan,
            so_lop_du_kien=1,  # Default
            giang_vien_id=request.ma_giang_vien if request.ma_giang_vien else None
        )
        
        if success:
            return ServiceResult.ok(
                message="Đã tạo đề xuất học phần thành công",
                data=None
            )
        else:
            return ServiceResult.fail("Không thể tạo đề xuất học phần")
