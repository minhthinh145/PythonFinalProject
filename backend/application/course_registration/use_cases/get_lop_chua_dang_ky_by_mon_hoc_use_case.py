from typing import List, Dict, Any
from core.types import ServiceResult
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository
)

class GetLopChuaDangKyByMonHocUseCase:
    def __init__(
        self,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        dang_ky_hp_repo: IDangKyHocPhanRepository
    ):
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.dang_ky_hp_repo = dang_ky_hp_repo

    def execute(self, sinh_vien_id: str, mon_hoc_id: str, hoc_ky_id: str) -> ServiceResult:
        if not sinh_vien_id or not mon_hoc_id or not hoc_ky_id:
            return ServiceResult.fail(
                "Thiếu thông tin (sinh viên, môn học, học kỳ)", 
                error_code="MISSING_PARAMS"
            )

        # 1. Get all classes for this subject in this semester
        all_classes = self.lop_hoc_phan_repo.get_by_mon_hoc_and_hoc_ky(mon_hoc_id, hoc_ky_id)
        
        # 2. Get registered classes for this subject (to exclude)
        registered_classes = self.dang_ky_hp_repo.get_registered_classes_by_subject(
            sinh_vien_id, mon_hoc_id, hoc_ky_id
        )
        registered_class_ids = {str(reg.lop_hoc_phan.id) if hasattr(reg, 'lop_hoc_phan') else str(reg.id) for reg in registered_classes}
        # Note: registered_classes returns DangKyHocPhan objects, which have lop_hoc_phan relation.
        # But in test mock, we might return LopHocPhan objects directly if not careful.
        # Let's adjust logic to be safe.
        
        # Actually, let's look at the repo implementation:
        # get_registered_classes_by_subject returns List[DangKyHocPhan]
        # So we need reg.lop_hoc_phan.id
        
        registered_lhp_ids = set()
        for reg in registered_classes:
            if hasattr(reg, 'lop_hoc_phan'):
                registered_lhp_ids.add(str(reg.lop_hoc_phan.id))
            elif hasattr(reg, 'id'): # Fallback if mock returns LHP directly (though it shouldn't)
                 registered_lhp_ids.add(str(reg.id))

        # 3. Filter and Format
        result_data = []
        for lhp in all_classes:
            if str(lhp.id) in registered_lhp_ids:
                continue
                
            # Format DTO
            item = {
                "id": str(lhp.id),
                "maLop": lhp.ma_lop,
                "tenLop": lhp.ten_lop_hoc_phan if hasattr(lhp, 'ten_lop_hoc_phan') else lhp.ma_lop, # Fallback
                "soLuongHienTai": lhp.so_luong_hien_tai,
                "soLuongToiDa": lhp.so_luong_toi_da,
                "trangThai": "con_cho" if (lhp.so_luong_hien_tai or 0) < (lhp.so_luong_toi_da or 50) else "day",
                "giangVien": lhp.giang_vien.ho_ten if lhp.giang_vien else "Chưa phân công",
                "tkb": []
            }
            
            # Add schedule info
            if hasattr(lhp, 'lichhocdinhky_set'):
                for lich in lhp.lichhocdinhky_set.all():
                    item["tkb"].append({
                        "thu": lich.thu,
                        "tietBatDau": lich.tiet_bat_dau,
                        "tietKetThuc": lich.tiet_ket_thuc,
                        "phong": lich.phong.ma_phong if lich.phong else ""
                    })
            
            result_data.append(item)

        return ServiceResult.ok(result_data)
