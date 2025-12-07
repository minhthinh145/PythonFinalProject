"""
Reset Demo Data Use Case
Clears all test/demo data while preserving master data
"""
from django.db import connections
from core.types import ServiceResult
import logging

logger = logging.getLogger(__name__)


class ResetDemoDataUseCase:
    """
    Use case to reset demo data for testing/demonstration
    Preserves: users, mon_hoc, khoa, phong, hoc_ky, nien_khoa, etc.
    Clears: registrations, payments, schedules, proposals, etc.
    """
    
    def execute(self, confirm_reset: bool = False) -> ServiceResult:
        """
        Execute the reset operation
        
        Args:
            confirm_reset: Must be True to proceed (safety check)
        """
        if not confirm_reset:
            return ServiceResult.fail(
                "Phải xác nhận reset (confirmReset=true)",
                error_code="CONFIRMATION_REQUIRED"
            )
        
        try:
            # Use 'neon' database connection (PostgreSQL), NOT default (SQLite)
            with connections['neon'].cursor() as cursor:
                # Execute TRUNCATE in order respecting FK constraints
                tables_to_clear = [
                    # Step 1: Payment & Học phí
                    'payment_ipn_logs',
                    'payment_transactions',
                    'chi_tiet_hoc_phi',
                    'mien_giam_hoc_phi',
                    'hoc_phi',
                    'chinh_sach_tin_chi',
                    
                    # Step 2: Lịch sử & Đăng ký HP
                    'chi_tiet_lich_su_dang_ky',
                    'lich_su_dang_ky',
                    'dang_ky_tkb',
                    'dang_ky_hoc_phan',
                    
                    # Step 3: Ghi danh
                    'ghi_danh_hoc_phan',
                    
                    # Step 4: Tài liệu & Thông báo
                    'thong_bao_nguoi_nhan',
                    'thong_bao',
                    'tai_lieu',
                    
                    # Step 5: LopHocPhan & HocPhan
                    'ket_qua_hoc_phan',
                    'lich_day_lop_hoc_phan',
                    'lich_hoc_dinh_ky',
                    'lich_su_xoa_lop_hoc_phan',
                    'lop_hoc_phan',
                    'hoc_phan',
                    
                    # Step 6: Đề xuất Học phần
                    'de_xuat_hoc_phan_log',
                    'de_xuat_hoc_phan_gv',
                    'de_xuat_hoc_phan',
                    
                    # Step 7: Phase & Dot Dang Ky
                    'dot_dang_ky',
                    'ky_phase',
                ]
                
                cleared_tables = []
                errors = []
                
                for table in tables_to_clear:
                    try:
                        cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                        cleared_tables.append(table)
                        logger.info(f"✅ Cleared table: {table}")
                    except Exception as e:
                        error_msg = f"Failed to clear {table}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(f"❌ {error_msg}")
                
                # Clear MongoDB
                mongo_cleared = self._clear_mongodb()
            
            return ServiceResult.ok({
                "clearedTables": cleared_tables,
                "errors": errors,
                "mongoCleared": mongo_cleared,
                "totalCleared": len(cleared_tables)
            }, f"Reset thành công {len(cleared_tables)} bảng")
            
        except Exception as e:
            logger.error(f"Reset failed: {e}")
            return ServiceResult.fail(
                f"Lỗi khi reset data: {str(e)}",
                error_code="RESET_FAILED"
            )
    
    def _clear_mongodb(self) -> bool:
        """Clear MongoDB TKB collections"""
        try:
            from infrastructure.persistence.mongodb_service import get_mongodb_service
            mongo = get_mongodb_service()
            
            if not mongo.is_available:
                logger.warning("MongoDB not available, skipping")
                return False
            
            # Clear TKB collections
            mongo.db['thoi_khoa_bieu_mon_hoc'].delete_many({})
            mongo.db['tkb_cache'].delete_many({})
            mongo.db['tai_lieu'].delete_many({})
            
            logger.info("✅ MongoDB TKB data cleared")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB clear failed: {e}")
            return False
