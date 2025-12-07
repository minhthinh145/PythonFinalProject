"""
Infrastructure Layer - TLK Repository Implementation
"""
from typing import List, Optional
from django.db.models import Count
import uuid
from datetime import datetime, timezone

from application.tlk.interfaces import (
    ITLKRepository,
    ITLKHocPhanRepository,
    ITLKDeXuatRepository,
    TLKMonHocDTO,
    TLKGiangVienDTO,
    TLKPhongHocDTO,
    TLKHocPhanForCreateLopDTO,
    TLKDeXuatHocPhanDTO,
)
from infrastructure.persistence.models import (
    TroLyKhoa,
    MonHoc,
    GiangVien,
    Users,
    Phong,
    HocPhan,
    HocKy,
    LopHocPhan,
    LichHocDinhKy,
    GhiDanhHocPhan,
    DeXuatHocPhan,
)
from infrastructure.persistence.mongodb_service import MongoDBService


class TLKRepository(ITLKRepository):
    """
    Repository implementation for TLK base operations
    """
    
    def __init__(self):
        self.mongo_service = MongoDBService()
    
    def get_khoa_id_by_user(self, user_id: str) -> Optional[str]:
        """Get khoa_id from TLK user"""
        try:
            tlk = TroLyKhoa.objects.using('neon').get(id=user_id)
            return str(tlk.khoa_id)
        except TroLyKhoa.DoesNotExist:
            return None
    
    def get_mon_hoc_by_khoa(self, khoa_id: str) -> List[TLKMonHocDTO]:
        """Get all Mon Hoc belonging to a Khoa"""
        mon_hocs = MonHoc.objects.using('neon').filter(
            khoa_id=khoa_id
        ).order_by('ma_mon')
        
        return [
            TLKMonHocDTO(
                id=str(mh.id),
                ma_mon=mh.ma_mon,
                ten_mon=mh.ten_mon,
                so_tin_chi=mh.so_tin_chi,
            )
            for mh in mon_hocs
        ]
    
    def get_giang_vien_by_khoa(self, khoa_id: str) -> List[TLKGiangVienDTO]:
        """Get all Giang Vien belonging to a Khoa"""
        giang_viens = GiangVien.objects.using('neon').select_related(
            'id'  # Users table
        ).filter(
            khoa_id=khoa_id
        ).order_by('id__ho_ten')
        
        return [
            TLKGiangVienDTO(
                id=str(gv.id.id),
                ho_ten=gv.id.ho_ten,
            )
            for gv in giang_viens
        ]
    
    def get_phong_hoc_by_khoa(self, khoa_id: str) -> List[TLKPhongHocDTO]:
        """Get all Phong Hoc associated with TLK's khoa"""
        phongs = Phong.objects.using('neon').select_related('co_so').filter(
            khoa_id=khoa_id
        ).order_by('ma_phong')
        
        return [
            TLKPhongHocDTO(
                id=str(ph.id),
                ma_phong=ph.ma_phong,
                ten_co_so=ph.co_so.ten_co_so if ph.co_so else None,
                suc_chua=ph.suc_chua,
            )
            for ph in phongs
        ]
    
    def get_available_phong_hoc(self, khoa_id: str) -> List[TLKPhongHocDTO]:
        """Get available (unassigned) Phong Hoc"""
        # Get all available phong (da_dc_su_dung=False or NULL) associated with khoa
        phongs = Phong.objects.using('neon').select_related('co_so').filter(
            khoa_id=khoa_id,
            da_dc_su_dung__in=[False, None]
        ).order_by('ma_phong')
        
        return [
            TLKPhongHocDTO(
                id=str(ph.id),
                ma_phong=ph.ma_phong,
                ten_co_so=ph.co_so.ten_co_so if ph.co_so else None,
                suc_chua=ph.suc_chua,
            )
            for ph in phongs
        ]


class TLKHocPhanRepository(ITLKHocPhanRepository):
    """
    Repository implementation for TLK HocPhan/LopHocPhan operations
    """
    
    def get_hoc_phans_for_create_lop(
        self, 
        hoc_ky_id: str, 
        khoa_id: str
    ) -> List[TLKHocPhanForCreateLopDTO]:
        """
        Get all approved DeXuatHocPhan for creating Lop Hoc Phan.
        
        BUSINESS LOGIC (from BE legacy):
        - Each DeXuat = 1 class with specific GiangVien
        - Students choose which GV they want -> enroll in that class
        - Do NOT group by mon_hoc - return ALL approved de_xuat as separate classes
        """
        # Get approved de xuat in this hoc_ky for this khoa
        # trang_thai='da_duyet_pdt' means PDT has approved
        de_xuats = DeXuatHocPhan.objects.using('neon').select_related(
            'mon_hoc',
            'giang_vien_de_xuat',
            'giang_vien_de_xuat__id',  # Users
        ).filter(
            hoc_ky_id=hoc_ky_id,
            khoa_id=khoa_id,
            trang_thai='da_duyet_pdt'  # PDT approved
        ).order_by('mon_hoc__ma_mon', 'giang_vien_de_xuat__id__ho_ten')
        
        result = []
        
        for dx in de_xuats:
            # Get HocPhan for this mon_hoc and hoc_ky (use first() to handle duplicates)
            hoc_phan = HocPhan.objects.using('neon').filter(
                mon_hoc_id=dx.mon_hoc_id,
                id_hoc_ky_id=hoc_ky_id
            ).first()
            
            if not hoc_phan:
                # Skip if no HocPhan created yet
                continue
            
            # Count ghi danh sinh vien for this specific GV's class
            # Note: GhiDanhHocPhan may need to filter by giang_vien if available
            sv_count = GhiDanhHocPhan.objects.using('neon').filter(
                hoc_phan_id=hoc_phan.id,
                trang_thai='da_ghi_danh'
            ).count()
            
            # Get giang vien info
            gv_name = None
            gv_id = None
            if dx.giang_vien_de_xuat:
                gv_id = str(dx.giang_vien_de_xuat.id.id)
                gv_name = dx.giang_vien_de_xuat.id.ho_ten
            
            # Use ten_mon from MonHoc as ten_hoc_phan (more reliable than HocPhan.ten_hoc_phan)
            ten_hoc_phan = dx.mon_hoc.ten_mon if dx.mon_hoc else hoc_phan.ten_hoc_phan
            
            result.append(TLKHocPhanForCreateLopDTO(
                id=str(dx.id),  # de_xuat_id - unique key for FE
                hoc_phan_id=str(hoc_phan.id),  # actual hoc_phan.id
                ma_hoc_phan=dx.mon_hoc.ma_mon,
                ten_hoc_phan=ten_hoc_phan,
                so_tin_chi=dx.mon_hoc.so_tin_chi,
                so_sinh_vien_ghi_danh=sv_count,
                ten_giang_vien=gv_name,
                giang_vien_id=gv_id,
            ))
        
        return result


class TLKDeXuatRepository(ITLKDeXuatRepository):
    """
    Repository implementation for TLK De Xuat Hoc Phan operations
    """
    
    def get_de_xuat_by_khoa(
        self, 
        khoa_id: str, 
        hoc_ky_id: Optional[str] = None
    ) -> List[TLKDeXuatHocPhanDTO]:
        """Get De Xuat Hoc Phan created by TLK of a Khoa"""
        query = DeXuatHocPhan.objects.using('neon').select_related(
            'mon_hoc',
            'giang_vien_de_xuat',
            'giang_vien_de_xuat__id',
        ).filter(
            khoa_id=khoa_id
        )
        
        if hoc_ky_id:
            query = query.filter(hoc_ky_id=hoc_ky_id)
        
        de_xuats = query.order_by('-created_at')
        
        return [
            TLKDeXuatHocPhanDTO(
                id=str(dx.id),
                ma_hoc_phan=dx.mon_hoc.ma_mon,
                ten_hoc_phan=dx.mon_hoc.ten_mon,
                so_tin_chi=dx.mon_hoc.so_tin_chi,
                giang_vien=dx.giang_vien_de_xuat.id.ho_ten if dx.giang_vien_de_xuat else None,
                trang_thai=dx.trang_thai or 'cho_duyet',
            )
            for dx in de_xuats
        ]
    
    def create_de_xuat(
        self,
        khoa_id: str,
        nguoi_tao_id: str,
        hoc_ky_id: str,
        mon_hoc_id: str,
        so_lop_du_kien: int,
        giang_vien_id: Optional[str] = None
    ) -> bool:
        """Create a new De Xuat Hoc Phan"""
        try:
            de_xuat = DeXuatHocPhan(
                id=uuid.uuid4(),
                khoa_id=khoa_id,
                nguoi_tao_id=nguoi_tao_id,
                hoc_ky_id=hoc_ky_id,
                mon_hoc_id=mon_hoc_id,
                so_lop_du_kien=so_lop_du_kien,
                giang_vien_de_xuat_id=giang_vien_id,
                trang_thai='cho_duyet',
                cap_duyet_hien_tai='truong_khoa',
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            de_xuat.save(using='neon')
            return True
        except Exception as e:
            import logging
            logging.error(f"Failed to create de xuat: {e}")
            return False


class TLKThoiKhoaBieuRepository:
    """
    Repository for TKB operations by TLK
    """
    
    def __init__(self):
        self.mongo_service = MongoDBService()
    
    def get_hoc_ky_hien_hanh(self) -> Optional[str]:
        """Get current học kỳ ID"""
        try:
            hoc_ky = HocKy.objects.using('neon').filter(
                trang_thai_hien_tai=True
            ).first()
            return str(hoc_ky.id) if hoc_ky else None
        except Exception:
            return None
    
    def get_tkb_by_hoc_phans(
        self, 
        ma_hoc_phans: List[str], 
        hoc_ky_id: str
    ) -> List[dict]:
        """
        Get TKB data for multiple học phần from MongoDB
        Returns list of {maHocPhan, id, danhSachLop} with camelCase keys for FE
        """
        # Get data from MongoDB with camelCase transformation
        tkb_list = self.mongo_service.get_tkb_by_hoc_phans(ma_hoc_phans, hoc_ky_id, transform_to_camel=True)
        
        result = []
        for tkb_data in tkb_list:
            ma_hp = tkb_data.get('maHocPhan')  # Now in camelCase from transformer
            
            # Get HocPhan ID for response
            hoc_phan = HocPhan.objects.using('neon').filter(
                mon_hoc__ma_mon=ma_hp,
                id_hoc_ky_id=hoc_ky_id
            ).first()
            
            result.append({
                'id': str(hoc_phan.id) if hoc_phan else None,
                'maHocPhan': ma_hp,
                'danhSachLop': tkb_data.get('danhSachLop', [])  # Also in camelCase
            })
        
        return result
    
    def xep_thoi_khoa_bieu(
        self,
        ma_hoc_phan: str,
        hoc_ky_id: str,
        danh_sach_lop: List[dict],
        giang_vien_id: Optional[str] = None
    ) -> dict:
        """
        Create/Update TKB for a học phần
        
        Args:
            ma_hoc_phan: Mã học phần
            hoc_ky_id: Học kỳ ID
            danh_sach_lop: List of {tenLop, phongHocId, ngayBatDau, ngayKetThuc, tietBatDau, tietKetThuc, thuTrongTuan}
            giang_vien_id: Optional giảng viên ID
        
        Returns:
            {success: bool, message: str, created_count: int}
        """
        import logging
        logging.info(f"🔵 xep_thoi_khoa_bieu called: ma_hoc_phan={ma_hoc_phan}, hoc_ky_id={hoc_ky_id}, len(danh_sach_lop)={len(danh_sach_lop)}")
        
        # Step 1: Find MonHoc by ma_mon
        try:
            mon_hoc = MonHoc.objects.using('neon').get(ma_mon=ma_hoc_phan)
        except MonHoc.DoesNotExist:
            return {'success': False, 'message': f'Môn học {ma_hoc_phan} không tồn tại', 'created_count': 0}
        
        # Step 2: Find or Create HocPhan
        try:
            hoc_phan = HocPhan.objects.using('neon').select_related('mon_hoc').get(
                mon_hoc_id=mon_hoc.id,
                id_hoc_ky_id=hoc_ky_id
            )
        except HocPhan.DoesNotExist:
            # Auto-create HocPhan if not exists (matching BE legacy logic)
            hoc_phan = HocPhan(
                id=uuid.uuid4(),
                mon_hoc_id=mon_hoc.id,
                ten_hoc_phan=mon_hoc.id,  # Same as legacy: ten_hoc_phan = mon_hoc_id
                trang_thai_mo=True,
                id_hoc_ky_id=hoc_ky_id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            hoc_phan.save(using='neon')
        
        created_count = 0
        processed_count = 0  # Track all processed schedules
        
        for lop_data in danh_sach_lop:
            try:
                # Check if lop exists (by id or tenLop)
                lop_id = lop_data.get('id')
                ten_lop = lop_data.get('tenLop')
                
                if lop_id:
                    try:
                        lop = LopHocPhan.objects.using('neon').get(id=lop_id)
                    except LopHocPhan.DoesNotExist:
                        lop = None
                else:
                    lop = LopHocPhan.objects.using('neon').filter(
                        hoc_phan_id=hoc_phan.id,
                        ma_lop=ten_lop
                    ).first()
                
                if not lop:
                    # Parse dates from ISO format to YYYY-MM-DD
                    ngay_bat_dau = lop_data.get('ngayBatDau')
                    ngay_ket_thuc = lop_data.get('ngayKetThuc')
                    
                    if ngay_bat_dau and isinstance(ngay_bat_dau, str):
                        ngay_bat_dau = ngay_bat_dau.split('T')[0]  # Extract YYYY-MM-DD from ISO datetime
                    if ngay_ket_thuc and isinstance(ngay_ket_thuc, str):
                        ngay_ket_thuc = ngay_ket_thuc.split('T')[0]
                    
                    # Create new LopHocPhan
                    lop = LopHocPhan(
                        id=uuid.uuid4(),
                        hoc_phan_id=hoc_phan.id,
                        ma_lop=ten_lop or f"{ma_hoc_phan}_{created_count + 1}",
                        giang_vien_id=giang_vien_id,
                        so_luong_toi_da=50,  # Default
                        so_luong_hien_tai=0,
                        phong_mac_dinh_id=lop_data.get('phongHocId'),
                        trang_thai_lop='dang_mo',  # Valid values: dang_mo, dong, huy
                        ngay_bat_dau=ngay_bat_dau,
                        ngay_ket_thuc=ngay_ket_thuc,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    lop.save(using='neon')
                    created_count += 1
                
                # NOTE: Lịch học KHÔNG lưu vào PostgreSQL table lich_hoc_dinh_ky
                # Chỉ lưu vào MongoDB (xem logic save_tkb_mon_hoc bên dưới)
                
                processed_count += 1
                
            except Exception as e:
                import logging
                logging.error(f"Error creating lop: {e}")
                continue
        
        # Save TKB to MongoDB (PRIMARY storage for schedules)
        # ALWAYS save MongoDB even if LopHocPhan already exists (we're adding schedules)
        if processed_count > 0:
            import logging
            logging.info(f"Saving {processed_count} schedule(s) to MongoDB (created {created_count} new classes)...")
            try:
                self.mongo_service.save_tkb_mon_hoc(
                    ma_hoc_phan=ma_hoc_phan,
                    hoc_ky_id=hoc_ky_id,
                    danh_sach_lop=danh_sach_lop
                )
                logging.info(f"✅ Successfully saved TKB to MongoDB")
            except Exception as e:
                logging.error(f"❌ Failed to save TKB to MongoDB: {e}")
        
        return {
            'success': True,
            'message': f'Đã tạo {created_count} lớp học phần',
            'created_count': created_count
        }
