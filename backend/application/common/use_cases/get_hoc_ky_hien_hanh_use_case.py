"""
Application Layer - Get Hoc Ky Hien Hanh Use Case

Ported from be-legacy Clean Architecture:
- src/application/use-cases/hocKyPublic/GetHocKyHienHanh.usecase.ts

Logic:
1. Query HocKy where hien_hanh = True
2. If found, fetch related NienKhoa
3. Map to DTO format matching FE expectations
"""
from typing import Optional, Dict, Any
from core.types import ServiceResult
from application.common.interfaces import IHocKyRepository, INienKhoaRepository


class GetHocKyHienHanhUseCase:
    """
    Use case to get the current active semester
    """
    
    def __init__(
        self,
        hoc_ky_repo: IHocKyRepository,
        nien_khoa_repo: INienKhoaRepository
    ):
        self.hoc_ky_repo = hoc_ky_repo
        self.nien_khoa_repo = nien_khoa_repo
        
    def execute(self) -> ServiceResult:
        """
        Execute logic to get current semester
        
        Returns:
            ServiceResult with HocKyHienHanhDTO or null if not found
            
        FE expects (from commonApi.ts):
        {
            id: string,
            tenHocKy: string,
            maHocKy: number,
            nienKhoa: {
                id: string,
                tenNienKhoa: string
            },
            ngayBatDau: string | null,
            ngayKetThuc: string | null
        }
        """
        try:
            # Query for current semester
            hoc_ky = self.hoc_ky_repo.find_hien_hanh()
            
            if not hoc_ky:
                # Return success with null data (not 404)
                return ServiceResult.ok(None, "Không có học kỳ hiện hành")
            
            # Fetch related NienKhoa
            nien_khoa = self.nien_khoa_repo.find_by_id(hoc_ky.id_nien_khoa_id)
            
            # Map to DTO
            data: Dict[str, Any] = {
                'id': str(hoc_ky.id),
                'tenHocKy': hoc_ky.ten_hoc_ky,
                'maHocKy': hoc_ky.ma_hoc_ky,
                'nienKhoa': {
                    'id': str(nien_khoa.id) if nien_khoa else str(hoc_ky.id_nien_khoa_id),
                    'tenNienKhoa': nien_khoa.ten_nien_khoa if nien_khoa else ""
                },
                'ngayBatDau': hoc_ky.ngay_bat_dau.isoformat() if hoc_ky.ngay_bat_dau else None,
                'ngayKetThuc': hoc_ky.ngay_ket_thuc.isoformat() if hoc_ky.ngay_ket_thuc else None
            }
            
            return ServiceResult.ok(data, "Lấy học kỳ hiện hành thành công")
            
        except Exception as e:
            return ServiceResult.fail(
                f"Lỗi khi lấy học kỳ hiện hành: {str(e)}",
                error_code="GET_HOC_KY_HIEN_HANH_FAILED"
            )
