"""
Application Layer - Get Mon Hoc Ghi Danh Use Case
"""
from typing import Optional
from core.types import ServiceResult
from application.enrollment.interfaces import (
    IHocKyRepository,
    IHocPhanRepository
)

class GetMonHocGhiDanhUseCase:
    """
    Use case to get list of subjects available for enrollment
    """
    
    def __init__(
        self,
        hoc_ky_repo: IHocKyRepository,
        hoc_phan_repo: IHocPhanRepository
    ):
        self.hoc_ky_repo = hoc_ky_repo
        self.hoc_phan_repo = hoc_phan_repo
        
    def execute(self, hoc_ky_id: Optional[str] = None) -> ServiceResult:
        """
        Execute logic
        """
        target_hoc_ky_id = hoc_ky_id
        
        if not target_hoc_ky_id:
            hoc_ky_hien_hanh = self.hoc_ky_repo.get_current_hoc_ky()
            if not hoc_ky_hien_hanh:
                return ServiceResult.fail(
                    "Không có học kỳ hiện hành", 
                    error_code="HOC_KY_HIEN_HANH_NOT_FOUND"
                )
            target_hoc_ky_id = hoc_ky_hien_hanh.id
            
        # Get open subjects
        hoc_phan_list = self.hoc_phan_repo.find_all_open(target_hoc_ky_id)
        
        # Map to DTO
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[GetMonHocGhiDanhUseCase] Processing {len(hoc_phan_list)} hoc_phan records")
        
        data = []
        for hp in hoc_phan_list:
            try:
                logger.info(f"[GetMonHocGhiDanhUseCase] Processing hp.id={hp.id}, ten={hp.ten_hoc_phan}")
                
                # Handle relationship access safely
                mon_hoc = hp.mon_hoc
                logger.info(f"[GetMonHocGhiDanhUseCase] mon_hoc={mon_hoc.id if mon_hoc else None}, ten_mon={mon_hoc.ten_mon if mon_hoc else None}")
                
                # Query correct de_xuat: same mon_hoc + hoc_ky + approved by PDT
                de_xuat = mon_hoc.dexuathocphan_set.filter(
                    hoc_ky_id=hp.id_hoc_ky_id,  # Same semester as HocPhan
                    trang_thai='da_duyet_pdt'   # Only approved ones
                ).order_by('-created_at').first() if mon_hoc else None
                logger.info(f"[GetMonHocGhiDanhUseCase] de_xuat found: {de_xuat.id if de_xuat else None}")
                
                ten_giang_vien = "Chưa có giảng viên"
                try:
                    # Access giang_vien_de_xuat may throw DoesNotExist if GV record was deleted
                    if de_xuat:
                        gv = de_xuat.giang_vien_de_xuat  # This line throws the error!
                        if gv and gv.id:
                            ten_giang_vien = gv.id.ho_ten
                except Exception as e:
                    logger.warning(f"[GetMonHocGhiDanhUseCase] GiangVien error: {e}")
                    # Continue with default value
                    
                data.append({
                    'id': str(hp.id),
                    'maMonHoc': mon_hoc.ma_mon if mon_hoc else "",
                    'tenMonHoc': mon_hoc.ten_mon if mon_hoc else "",
                    'soTinChi': mon_hoc.so_tin_chi if mon_hoc else 0,
                    'tenKhoa': mon_hoc.khoa.ten_khoa if mon_hoc and mon_hoc.khoa else "",
                    'tenGiangVien': ten_giang_vien
                })
                logger.info(f"[GetMonHocGhiDanhUseCase] Added to result: {mon_hoc.ten_mon if mon_hoc else 'N/A'}")
            except Exception as e:
                # Skip this hoc_phan if any error occurs
                logger.error(f"[GetMonHocGhiDanhUseCase] Error processing hp.id={hp.id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        logger.info(f"[GetMonHocGhiDanhUseCase] Final result count: {len(data)}")
            
        return ServiceResult.ok(data, "Lấy danh sách môn học ghi danh thành công")
