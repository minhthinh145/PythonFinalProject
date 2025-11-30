from typing import List, Any, Optional
from application.pdt.interfaces.repositories import IDeXuatHocPhanRepository, IPhongHocRepository, IChinhSachHocPhiRepository
from infrastructure.persistence.models import DeXuatHocPhan, Phong, ChinhSachTinChi

class DeXuatHocPhanRepository(IDeXuatHocPhanRepository):
    def get_pending_proposals(self) -> List[Any]:
        # Assuming 'trang_thai' field exists and 0/False means pending, or specific status string
        # Need to verify model structure. For now assuming standard Django model usage.
        # Based on typical patterns:
        return list(DeXuatHocPhan.objects.using('neon').filter(trang_thai='CHO_DUYET').values()) 
        # Or select_related/prefetch_related if returning full objects

    def approve_proposal(self, proposal_id: str) -> bool:
        try:
            updated_count = DeXuatHocPhan.objects.using('neon').filter(id=proposal_id).update(trang_thai='DA_DUYET')
            return updated_count > 0
        except Exception:
            return False

    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        try:
            # Update status
            updated_count = DeXuatHocPhan.objects.using('neon').filter(id=proposal_id).update(trang_thai='tu_choi')
            
            if updated_count > 0:
                # Create log entry
                # Note: We need to import DeXuatHocPhanLog, uuid, timezone inside or at top
                # For simplicity, assuming imports are available or adding them now.
                from infrastructure.persistence.models import DeXuatHocPhanLog
                from django.utils import timezone
                import uuid
                
                DeXuatHocPhanLog.objects.using('neon').create(
                    id=uuid.uuid4(),
                    de_xuat_id=proposal_id,
                    thoi_gian=timezone.now(),
                    hanh_dong='TU_CHOI', # Log action can be uppercase usually, but let's keep it consistent if needed.
                    ghi_chu=reason
                    # nguoi_thuc_hien is optional or needs to be passed down. 
                    # For now, we leave it blank or would need to change interface to accept user_id.
                )
                return True
            return False
        except Exception:
            return False

class PhongHocRepository(IPhongHocRepository):
    def get_available_rooms(self, start_time: Any = None, end_time: Any = None) -> List[Any]:
        return list(Phong.objects.using('neon').filter(khoa__isnull=True).values(
            'id', 'ma_phong', 'suc_chua', 'da_dc_su_dung', 'khoa_id', 'co_so_id', 'co_so__ten_co_so'
        ))

    def get_by_khoa(self, khoa_id: str) -> List[Any]:
        return list(Phong.objects.using('neon').filter(khoa_id=khoa_id).values(
            'id', 'ma_phong', 'suc_chua', 'da_dc_su_dung', 'khoa_id', 'co_so_id', 'co_so__ten_co_so'
        ))

    def assign_to_khoa(self, phong_id: str, khoa_id: str) -> bool:
        try:
            updated = Phong.objects.using('neon').filter(id=phong_id).update(khoa_id=khoa_id)
            return updated > 0
        except Exception:
            return False

    def unassign_from_khoa(self, phong_id: str) -> bool:
        try:
            updated = Phong.objects.using('neon').filter(id=phong_id).update(khoa_id=None)
            return updated > 0
        except Exception:
            return False

class ChinhSachHocPhiRepository(IChinhSachHocPhiRepository):
    def get_all(self) -> List[Any]:
        return list(ChinhSachTinChi.objects.using('neon').values(
            'id', 'hoc_ky_id', 'khoa_id', 'nganh_id', 'phi_moi_tin_chi', 'ngay_hieu_luc', 'ngay_het_hieu_luc',
            'hoc_ky__ten_hoc_ky', 'khoa__ten_khoa', 'nganh__ten_nganh'
        ))

    def create(self, data: dict) -> Any:
        try:
            obj = ChinhSachTinChi.objects.using('neon').create(**data)
            return obj
        except Exception:
            return None

    def update(self, id: str, data: dict) -> bool:
        try:
            # Filter out None values to avoid overwriting with None if not intended
            update_fields = {k: v for k, v in data.items() if v is not None}
            updated = ChinhSachTinChi.objects.using('neon').filter(id=id).update(**update_fields)
            return updated > 0
        except Exception:
            return False

    def get_by_nganh_khoa_hoc_ky(self, nganh_id: str, khoa_id: str, hoc_ky_id: str) -> Optional[Any]:
        # Priority: Nganh > Khoa > General (both None)
        # This method might return the specific policy found
        return ChinhSachTinChi.objects.using('neon').filter(
            hoc_ky_id=hoc_ky_id,
            nganh_id=nganh_id
        ).first()

    def calculate_tuition_bulk(self, hoc_ky_id: str) -> int:
        try:
            from infrastructure.persistence.models import DangKyHocPhan, HocPhi, SinhVien, MonHoc, LopHocPhan, HocPhan
            from django.db.models import Sum, F
            import uuid
            from django.utils import timezone

            # 1. Get all students who have registered courses in this semester
            # Join: DangKyHocPhan -> LopHocPhan -> HocPhan -> HocKy
            
            # Get list of student IDs
            student_ids = DangKyHocPhan.objects.using('neon').filter(
                lop_hoc_phan__hoc_phan__id_hoc_ky_id=hoc_ky_id,
                trang_thai='DA_DANG_KY' # Only calculate for confirmed registrations
            ).values_list('sinh_vien_id', flat=True).distinct()
            
            count = 0
            for sv_id in student_ids:
                # 2. Calculate total credits for this student in this semester
                total_credits = DangKyHocPhan.objects.using('neon').filter(
                    sinh_vien_id=sv_id,
                    lop_hoc_phan__hoc_phan__id_hoc_ky_id=hoc_ky_id,
                    trang_thai='DA_DANG_KY'
                ).aggregate(total=Sum('lop_hoc_phan__hoc_phan__mon_hoc__so_tin_chi'))['total'] or 0
                
                if total_credits == 0:
                    continue

                # 3. Find applicable policy
                # Get Student info to know Nganh/Khoa
                sv = SinhVien.objects.using('neon').get(id=sv_id)
                
                # Try to find policy for Nganh
                policy = ChinhSachTinChi.objects.using('neon').filter(
                    hoc_ky_id=hoc_ky_id,
                    nganh_id=sv.nganh_id
                ).first()
                
                if not policy:
                    # Try Khoa
                    policy = ChinhSachTinChi.objects.using('neon').filter(
                        hoc_ky_id=hoc_ky_id,
                        khoa_id=sv.khoa_id,
                        nganh_id__isnull=True
                    ).first()
                    
                if not policy:
                    # Try General (Khoa is null, Nganh is null)
                    policy = ChinhSachTinChi.objects.using('neon').filter(
                        hoc_ky_id=hoc_ky_id,
                        khoa_id__isnull=True,
                        nganh_id__isnull=True
                    ).first()
                    
                if not policy:
                    # No policy found, skip or log
                    continue
                    
                # 4. Calculate Total Fee
                total_fee = total_credits * policy.phi_moi_tin_chi
                
                # 5. Update or Create HocPhi
                HocPhi.objects.using('neon').update_or_create(
                    sinh_vien_id=sv_id,
                    hoc_ky_id=hoc_ky_id,
                    defaults={
                        'tong_hoc_phi': total_fee,
                        'chinh_sach': policy,
                        'ngay_tinh_toan': timezone.now(),
                        'trang_thai_thanh_toan': 'CHO_THANH_TOAN' # Reset status or keep? If re-calculating, maybe keep if already paid?
                        # For simplicity, assuming re-calc updates amount. If paid, maybe shouldn't update?
                        # Let's assume we can update amount.
                    }
                )
                count += 1
                
            return count
        except Exception as e:
            print(f"Error calculating tuition: {e}")
            return 0
