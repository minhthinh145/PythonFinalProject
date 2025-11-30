"""
Application Layer - Dang Ky Hoc Phan Use Case
"""
from typing import List, Optional, Any
from core.types import ServiceResult
from django.db import transaction
from application.course_registration.interfaces import (
    ILopHocPhanRepository,
    IDangKyHocPhanRepository,
    IDangKyTKBRepository,
    ILichSuDangKyRepository
)
from infrastructure.persistence.enrollment.repositories import KyPhaseRepository
from infrastructure.persistence.sinh_vien.sinh_vien_repository import SinhVienRepository

class DangKyHocPhanUseCase:
    """
    Use case to register for a course class
    """
    
    def __init__(
        self,
        lop_hoc_phan_repo: ILopHocPhanRepository,
        dang_ky_hp_repo: IDangKyHocPhanRepository,
        dang_ky_tkb_repo: IDangKyTKBRepository,
        lich_su_repo: ILichSuDangKyRepository,
        ky_phase_repo: KyPhaseRepository,
        sinh_vien_repo: SinhVienRepository
    ):
        self.lop_hoc_phan_repo = lop_hoc_phan_repo
        self.dang_ky_hp_repo = dang_ky_hp_repo
        self.dang_ky_tkb_repo = dang_ky_tkb_repo
        self.lich_su_repo = lich_su_repo
        self.ky_phase_repo = ky_phase_repo
        self.sinh_vien_repo = sinh_vien_repo
        
    def execute(self, sinh_vien_id: str, lop_hoc_phan_id: str, hoc_ky_id: str) -> ServiceResult:
        """
        Execute registration logic
        """
        try:
            # 1. Validate Student
            sinh_vien = self.sinh_vien_repo.get_by_id(sinh_vien_id)
            if not sinh_vien:
                return ServiceResult.fail("Sinh viên không tồn tại", error_code="STUDENT_NOT_FOUND")

            # 2. Check Phase
            current_phase = self.ky_phase_repo.get_current_phase(hoc_ky_id)
            if not current_phase or current_phase.phase != "dang_ky_hoc_phan":
                return ServiceResult.fail(
                    "Không trong thời gian đăng ký học phần", 
                    error_code="INVALID_PHASE"
                )

            # 3. Get Class Info
            lhp = self.lop_hoc_phan_repo.find_by_id(lop_hoc_phan_id)
            if not lhp:
                return ServiceResult.fail("Lớp học phần không tồn tại", error_code="CLASS_NOT_FOUND")
                
            # 4. Check Max Quantity
            if (lhp.so_luong_hien_tai or 0) >= (lhp.so_luong_toi_da or 50):
                return ServiceResult.fail("Lớp học phần đã đầy", error_code="CLASS_FULL")
                
            # 5. Check if already registered for this subject
            mon_hoc_id = lhp.hoc_phan.mon_hoc_id
            if self.dang_ky_hp_repo.has_registered_mon_hoc_in_hoc_ky(sinh_vien_id, mon_hoc_id, hoc_ky_id):
                return ServiceResult.fail(
                    "Sinh viên đã đăng ký môn học này trong học kỳ", 
                    error_code="SUBJECT_ALREADY_REGISTERED"
                )
                
            # 6. Check Time Conflict
            new_schedules = list(lhp.lichhocdinhky_set.all())
            existing_registrations = self.dang_ky_tkb_repo.find_registered_lop_hoc_phans_by_hoc_ky(sinh_vien_id, hoc_ky_id)
            
            for reg in existing_registrations:
                existing_lhp = reg.lop_hoc_phan
                existing_schedules = existing_lhp.lichhocdinhky_set.all()
                
                if self._check_conflict(new_schedules, existing_schedules):
                    return ServiceResult.fail(
                        f"Trùng lịch học với lớp {existing_lhp.ma_lop}", 
                        error_code="TIME_CONFLICT"
                    )

            # 7. Perform Registration (Atomic)
            with transaction.atomic(using='neon'):
                # Create DangKyHocPhan
                dang_ky = self.dang_ky_hp_repo.create({
                    "sinh_vien_id": sinh_vien_id,
                    "lop_hoc_phan_id": lop_hoc_phan_id,
                    "trang_thai": "da_dang_ky"
                })
                
                # Create DangKyTkb
                self.dang_ky_tkb_repo.create({
                    "dang_ky_id": dang_ky.id,
                    "sinh_vien_id": sinh_vien_id,
                    "lop_hoc_phan_id": lop_hoc_phan_id
                })
                
                # Update Quantity
                self.lop_hoc_phan_repo.update_so_luong(lop_hoc_phan_id, 1)
                
                # Log History
                self.lich_su_repo.upsert_and_log(
                    sinh_vien_id, 
                    hoc_ky_id, 
                    str(dang_ky.id), 
                    "dang_ky"
                )
                
            return ServiceResult.ok(None, "Đăng ký học phần thành công")
            
        except Exception as e:
            print(f"Error registering course: {e}")
            return ServiceResult.fail("Lỗi hệ thống khi đăng ký học phần", error_code="INTERNAL_ERROR")

    def _check_conflict(self, schedules1: List[Any], schedules2: List[Any]) -> bool:
        """
        Check if any schedule in list 1 overlaps with list 2
        """
        for s1 in schedules1:
            for s2 in schedules2:
                # Check same day
                if s1.thu != s2.thu:
                    continue
                    
                # Check time overlap
                # Overlap if (Start1 < End2) and (Start2 < End1)
                if s1.tiet_bat_dau < s2.tiet_ket_thuc and s2.tiet_bat_dau < s1.tiet_ket_thuc:
                    return True
                    
        return False
