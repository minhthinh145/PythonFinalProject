from typing import List, Any, Optional
from application.pdt.interfaces.repositories import IDeXuatHocPhanRepository, IPhongHocRepository, IChinhSachHocPhiRepository
from infrastructure.persistence.models import DeXuatHocPhan, Phong, ChinhSachTinChi
import logging

logger = logging.getLogger(__name__)
class DeXuatHocPhanRepository(IDeXuatHocPhanRepository):
    def get_pending_proposals(self) -> List[Any]:
        """
        Get proposals that TK has approved (trang_thai='da_duyet_tk')
        Returns DTO format matching FE expectations:
        - id, maHocPhan, tenHocPhan, soTinChi, giangVien, trangThai
        """
        de_xuats = DeXuatHocPhan.objects.using('neon').select_related(
            'mon_hoc', 'giang_vien_de_xuat', 'giang_vien_de_xuat__id'
        ).filter(trang_thai='da_duyet_tk')
        
        results = []
        for dx in de_xuats:
            # Get giang vien name
            giang_vien_name = ""
            if dx.giang_vien_de_xuat:
                try:
                    giang_vien_name = dx.giang_vien_de_xuat.id.ho_ten
                except:
                    pass
            
            results.append({
                'id': str(dx.id),
                'maHocPhan': dx.mon_hoc.ma_mon if dx.mon_hoc else "",
                'tenHocPhan': dx.mon_hoc.ten_mon if dx.mon_hoc else "",
                'soTinChi': dx.mon_hoc.so_tin_chi if dx.mon_hoc else 0,
                'giangVien': giang_vien_name,
                'trangThai': dx.trang_thai or "",
            })
        
        return results

    def approve_proposal(self, proposal_id: str) -> bool:
        """
        PDT approves a proposal that has been approved by TK
        1. Changes trang_thai from 'da_duyet_tk' to 'da_duyet_pdt'
        2. Creates HocPhan from the MonHoc in the proposal
        """
        try:
            from infrastructure.persistence.models import HocPhan
            from django.utils import timezone
            import uuid
            
            # Get the de xuat with related mon_hoc and hoc_ky
            de_xuat = DeXuatHocPhan.objects.using('neon').select_related(
                'mon_hoc', 'hoc_ky'
            ).filter(
                id=proposal_id,
                trang_thai='da_duyet_tk'  # Must be approved by TK first
            ).first()
            
            if not de_xuat:
                return False
            
            # Update status to da_duyet_pdt
            de_xuat.trang_thai = 'da_duyet_pdt'
            de_xuat.updated_at = timezone.now()
            de_xuat.save(using='neon')
            
            # Check if HocPhan already exists for this mon_hoc + hoc_ky
            existing_hoc_phan = HocPhan.objects.using('neon').filter(
                mon_hoc=de_xuat.mon_hoc,
                id_hoc_ky=de_xuat.hoc_ky
            ).first()
            
            if not existing_hoc_phan:
                # Create new HocPhan
                HocPhan.objects.using('neon').create(
                    id=uuid.uuid4(),
                    mon_hoc=de_xuat.mon_hoc,
                    ten_hoc_phan=de_xuat.mon_hoc.ten_mon,
                    so_lop=de_xuat.so_lop_du_kien,
                    trang_thai_mo=True,
                    id_hoc_ky=de_xuat.hoc_ky,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
            else:
                # Update existing HocPhan (increase so_lop)
                existing_hoc_phan.so_lop = (existing_hoc_phan.so_lop or 0) + de_xuat.so_lop_du_kien
                existing_hoc_phan.updated_at = timezone.now()
                existing_hoc_phan.save(using='neon')
            
            return True
        except Exception as e:
            print(f"Error approving proposal: {e}")
            import traceback
            traceback.print_exc()
            return False

    def reject_proposal(self, proposal_id: str) -> bool:
        try:
            # Update status
            updated_count = DeXuatHocPhan.objects.using('neon').filter(id=proposal_id).update(trang_thai='tu_choi')
            
            if updated_count > 0:
                # Create log entry
                from infrastructure.persistence.models import DeXuatHocPhanLog
                from django.utils import timezone
                import uuid
                
                DeXuatHocPhanLog.objects.using('neon').create(
                    id=uuid.uuid4(),
                    de_xuat_id=proposal_id,
                    thoi_gian=timezone.now(),
                    hanh_dong='TU_CHOI'
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

    def batch_assign_to_khoa(self, phong_ids: list, khoa_id: str) -> int:
        """Batch assign multiple rooms to khoa. Returns count of updated rooms."""
        try:
            updated = Phong.objects.using('neon').filter(id__in=phong_ids).update(khoa_id=khoa_id)
            return updated
        except Exception:
            return 0

    def unassign_from_khoa(self, phong_id: str) -> bool:
        try:
            updated = Phong.objects.using('neon').filter(id=phong_id).update(khoa_id=None)
            return updated > 0
        except Exception:
            return False

    def batch_unassign_from_khoa(self, phong_ids: list) -> int:
        """Batch unassign multiple rooms from khoa. Returns count of updated rooms."""
        try:
            updated = Phong.objects.using('neon').filter(id__in=phong_ids).update(khoa_id=None)
            return updated
        except Exception:
            return 0

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

    def delete(self, id: str) -> bool:
        """Delete a ChinhSachTinChi by id"""
        try:
            deleted_count, _ = ChinhSachTinChi.objects.using('neon').filter(id=id).delete()
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete chinh_sach {id}: {e}")
            return False

    def calculate_tuition_bulk(self, hoc_ky_id: str) -> int:
        try:
            from infrastructure.persistence.models import DangKyHocPhan, HocPhi, SinhVien, MonHoc, LopHocPhan, HocPhan, ChiTietHocPhi
            from django.db.models import Sum, F
            import uuid
            from django.utils import timezone

            # 1. Get all students who have registered courses in this semester
            # Join: DangKyHocPhan -> LopHocPhan -> HocPhan -> HocKy
            
            # Get list of student IDs (use lowercase 'da_dang_ky')
            student_ids = DangKyHocPhan.objects.using('neon').filter(
                lop_hoc_phan__hoc_phan__id_hoc_ky_id=hoc_ky_id,
                trang_thai='da_dang_ky'  # lowercase to match DB values
            ).values_list('sinh_vien_id', flat=True).distinct()
            logger.info(f"Calculating tuition for {len(student_ids)} students in hoc_ky_id={hoc_ky_id}")
            count = 0
            for sv_id in student_ids:
                # 2. Get all registered courses for this student in this semester
                dang_ky_list = DangKyHocPhan.objects.using('neon').filter(
                    sinh_vien_id=sv_id,
                    lop_hoc_phan__hoc_phan__id_hoc_ky_id=hoc_ky_id,
                    trang_thai='da_dang_ky'  # lowercase to match DB values
                ).select_related('lop_hoc_phan__hoc_phan__mon_hoc')
                
                if not dang_ky_list:
                    continue
                    
                # Calculate total credits
                total_credits = sum(dk.lop_hoc_phan.hoc_phan.mon_hoc.so_tin_chi for dk in dang_ky_list)
                
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
                # Check if record exists first
                existing = HocPhi.objects.using('neon').filter(
                    sinh_vien_id=sv_id,
                    hoc_ky_id=hoc_ky_id
                ).first()
                
                if existing:
                    hoc_phi = existing
                    hoc_phi.tong_hoc_phi = total_fee
                    hoc_phi.chinh_sach = policy
                    hoc_phi.ngay_tinh_toan = timezone.now()
                    hoc_phi.save(using='neon')
                    # Delete old chi tiet to recreate
                    ChiTietHocPhi.objects.using('neon').filter(hoc_phi_id=hoc_phi.id).delete()
                else:
                    # Create new with UUID
                    hoc_phi = HocPhi.objects.using('neon').create(
                        id=uuid.uuid4(),
                        sinh_vien_id=sv_id,
                        hoc_ky_id=hoc_ky_id,
                        tong_hoc_phi=total_fee,
                        chinh_sach=policy,
                        ngay_tinh_toan=timezone.now(),
                        trang_thai_thanh_toan='chua_thanh_toan'  # lowercase to match DB constraint
                    )
                
                # 6. Create ChiTietHocPhi for each registered course
                for dk in dang_ky_list:
                    lop_hoc_phan = dk.lop_hoc_phan
                    mon_hoc = lop_hoc_phan.hoc_phan.mon_hoc
                    so_tin_chi = mon_hoc.so_tin_chi
                    phi_tin_chi = float(policy.phi_moi_tin_chi)
                    thanh_tien = so_tin_chi * phi_tin_chi
                    
                    ChiTietHocPhi.objects.using('neon').get_or_create(
                        hoc_phi_id=hoc_phi.id,
                        lop_hoc_phan_id=lop_hoc_phan.id,
                        defaults={
                            'id': uuid.uuid4(),
                            'so_tin_chi': so_tin_chi,
                            'phi_tin_chi': phi_tin_chi,
                            'thanh_tien': thanh_tien
                        }
                    )
                
                count += 1
                
            return count
        except Exception as e:
            print(f"Error calculating tuition: {e}")
            import traceback
            traceback.print_exc()
            return 0
