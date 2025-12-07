from core.types import ServiceResult
from application.course_registration.interfaces import ILichSuDangKyRepository

class GetLichSuDangKyUseCase:
    def __init__(self, lich_su_repo: ILichSuDangKyRepository):
        self.lich_su_repo = lich_su_repo

    def execute(self, sinh_vien_id: str, hoc_ky_id: str) -> ServiceResult:
        if not sinh_vien_id or not hoc_ky_id:
            return ServiceResult.fail(
                "Thiếu thông tin (sinh viên, học kỳ)",
                error_code="MISSING_PARAMS"
            )

        # Get history record
        lich_su = self.lich_su_repo.find_by_sinh_vien_and_hoc_ky(sinh_vien_id, hoc_ky_id)
        
        # FE expects this format:
        # {
        #   hocKy: { tenHocKy, maHocKy },
        #   ngayTao: string (ISO),
        #   lichSu: [{ thoiGian, hanhDong, monHoc: { maMon, tenMon, soTinChi }, lopHocPhan: { maLop, tenHocPhan } }]
        # }
        
        lichSu_items = []
        hoc_ky_info = {"tenHocKy": "", "maHocKy": ""}
        ngay_tao = None
        
        if lich_su:
            # Get hoc_ky info
            if hasattr(lich_su, 'hoc_ky') and lich_su.hoc_ky:
                hoc_ky_info = {
                    "tenHocKy": lich_su.hoc_ky.ten_hoc_ky,
                    "maHocKy": lich_su.hoc_ky.ma_hoc_ky
                }
            
            # Get ngay tao
            ngay_tao = lich_su.created_at.isoformat() if hasattr(lich_su, 'created_at') and lich_su.created_at else None
            
            # Build lichSu items
            # Support both Django QuerySet (with order_by) and plain lists returned by tests/mocks
            details = lich_su.chitietlichsudangky_set.all()
            if hasattr(details, 'order_by'):
                iterable_details = details.order_by('-thoi_gian')
            else:
                # details is likely a list; sort by thoi_gian field descending if possible
                try:
                    iterable_details = sorted(details, key=lambda d: getattr(d, 'thoi_gian', None) or '', reverse=True)
                except Exception:
                    iterable_details = details

            for detail in iterable_details:
                # Handle thoi_gian: may be datetime object or string
                thoi_gian_val = getattr(detail, 'thoi_gian', None)
                if thoi_gian_val and hasattr(thoi_gian_val, 'isoformat'):
                    thoi_gian_str = thoi_gian_val.isoformat()
                else:
                    thoi_gian_str = thoi_gian_val  # already a string or None
                
                item = {
                    "thoiGian": thoi_gian_str,
                    "hanhDong": getattr(detail, 'hanh_dong', None) or getattr(detail, 'hanhDong', None),
                    "monHoc": {
                        "maMon": "",
                        "tenMon": "",
                        "soTinChi": 0
                    },
                    "lopHocPhan": {
                        "maLop": "",
                        "tenHocPhan": ""
                    }
                }

                # Get lop_hoc_phan and mon_hoc info
                # Wrap in try-except to handle deleted DangKyHocPhan references
                dang_ky = None
                lhp = None
                try:
                    dang_ky = getattr(detail, 'dang_ky_hoc_phan', None) or getattr(detail, 'dangKyHocPhan', None)
                    if dang_ky:
                        lhp = getattr(dang_ky, 'lop_hoc_phan', None) or getattr(dang_ky, 'lopHocPhan', None)
                except Exception:
                    # DangKyHocPhan or LopHocPhan was deleted, continue with empty info
                    pass

                if lhp:
                    item["lopHocPhan"]["maLop"] = getattr(lhp, 'ma_lop', None) or getattr(lhp, 'maLop', '') or ''
                    if getattr(lhp, 'hoc_phan', None):
                        hp = lhp.hoc_phan
                        item["lopHocPhan"]["tenHocPhan"] = getattr(hp, 'ten_hoc_phan', None) or getattr(hp, 'tenHocPhan', '') or ''
                        if getattr(hp, 'mon_hoc', None):
                            mon_hoc = hp.mon_hoc
                            item["monHoc"]["maMon"] = getattr(mon_hoc, 'ma_mon', None) or getattr(mon_hoc, 'maMon', '') or ''
                            item["monHoc"]["tenMon"] = getattr(mon_hoc, 'ten_mon', None) or getattr(mon_hoc, 'tenMon', '') or ''
                            item["monHoc"]["soTinChi"] = getattr(mon_hoc, 'so_tin_chi', None) or getattr(mon_hoc, 'soTinChi', 0) or 0

                lichSu_items.append(item)

        result_data = {
            "hocKy": hoc_ky_info,
            "ngayTao": ngay_tao or "",
            "lichSu": lichSu_items,
            # Backwards compatibility for tests/older clients
            "logs": lichSu_items
        }

        return ServiceResult.ok(result_data)
