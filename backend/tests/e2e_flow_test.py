#!/usr/bin/env python3
"""
E2E Test Script for ĐKHP System
Tests all phases: Tiền ghi danh → Ghi danh → Sắp xếp TKB → Đăng ký HP → Bình thường

Usage:
    python tests/e2e_flow_test.py

Environment:
    Uses TEST_DB_* variables from .env.test for test_neondb connection
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Test Accounts
ACCOUNTS = {
    "sinh_vien": {"username": "49.01.104.145", "password": "123456"},
    "tlk": {"username": "tlk.cntt", "password": "12345"},
    "pdt": {"username": "pdt01", "password": "12345"},
    "tk": {"username": "tk.cntt", "password": "123456"},
    "gv": {"username": "GV001", "password": "123456"},
}

# Tokens will be stored here after login
TOKENS: Dict[str, str] = {}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    token: Optional[str] = None,
    expect_success: bool = True
) -> Dict:
    """Make an API call and return response"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        result = response.json() if response.content else {}
        
        logger.info(f"{method.upper()} {endpoint} → {response.status_code}")
        
        if expect_success and response.status_code >= 400:
            logger.error(f"❌ Request failed: {result}")
        elif response.status_code < 400:
            logger.debug(f"✅ Response: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
        
        result["_status_code"] = response.status_code
        return result
        
    except Exception as e:
        logger.error(f"❌ API call failed: {e}")
        return {"isSuccess": False, "message": str(e), "_status_code": 500}


def login(role: str) -> Optional[str]:
    """Login and get token for a role"""
    account = ACCOUNTS.get(role)
    if not account:
        logger.error(f"Unknown role: {role}")
        return None
    
    # Try different password options
    passwords_to_try = [account["password"], "12345", "123456", "password"]
    
    for password in passwords_to_try:
        result = api_call("POST", "auth/login", {
            "tenDangNhap": account["username"],
            "matKhau": password
        }, expect_success=False)
        
        logger.debug(f"Login attempt {account['username']}/{password}: {result}")
        
        # Check various response formats
        token = None
        
        if result.get("isSuccess") and result.get("data", {}).get("accessToken"):
            token = result["data"]["accessToken"]
        elif result.get("accessToken"):
            token = result["accessToken"]
        elif result.get("data", {}).get("token"):
            token = result["data"]["token"]
        elif result.get("token"):
            token = result["token"]
        
        if token:
            TOKENS[role] = token
            logger.info(f"✅ Logged in as {role} ({account['username']}) with password '{password}'")
            return token
    
    # If all failed, print the last response for debugging
    logger.error(f"❌ Failed to login as {role} ({account['username']})")
    logger.error(f"   Last response: {result}")
    return None


def get_token(role: str) -> str:
    """Get token for role, login if needed"""
    if role not in TOKENS:
        login(role)
    return TOKENS.get(role, "")


# ============================================================================
# PHASE 0: SETUP - Query Database for Required Info
# ============================================================================

def phase_0_setup() -> Dict[str, Any]:
    """Get all required info from database"""
    logger.info("\n" + "="*60)
    logger.info("PHASE 0: SETUP - Getting Database Info")
    logger.info("="*60)
    
    context = {}
    token = get_token("pdt")
    
    # Get học kỳ hiện hành
    result = api_call("GET", "hoc-ky-hien-hanh", token=token)
    if result.get("isSuccess") and result.get("data"):
        context["hoc_ky"] = result["data"]
        logger.info(f"✅ Học kỳ hiện hành: {context['hoc_ky'].get('tenHocKy')}")
    else:
        logger.error("❌ Không lấy được học kỳ hiện hành")
        # Fallback - get all semesters and use first active one
        all_hk = api_call("GET", "hoc-ky-nien-khoa", token=token)
        if all_hk.get("data"):
            context["nien_khoa_list"] = all_hk["data"]
            logger.info(f"✅ Got {len(all_hk['data'])} niên khóa")
        return context
    
    # Get danh sách khoa
    result = api_call("GET", "pdt/khoa", token=token)
    if result.get("isSuccess") and result.get("data"):
        context["khoa_list"] = result["data"]
        # Find CNTT
        for khoa in result["data"]:
            if "CNTT" in khoa.get("tenKhoa", "").upper() or "CÔNG NGHỆ" in khoa.get("tenKhoa", "").upper():
                context["khoa_cntt"] = khoa
                logger.info(f"✅ Khoa CNTT: {khoa.get('tenKhoa')} (ID: {khoa.get('id')})")
                break
    
    # Get danh sách môn học
    result = api_call("GET", "pdt/mon-hoc?page=1&pageSize=100", token=token)
    if result.get("isSuccess") and result.get("data"):
        items = result["data"].get("items", result["data"]) if isinstance(result["data"], dict) else result["data"]
        context["mon_hoc_list"] = items[:10] if isinstance(items, list) else []
        logger.info(f"✅ Got {len(context.get('mon_hoc_list', []))} môn học")
    
    # Get danh sách giảng viên
    result = api_call("GET", "pdt/giang-vien", token=token)
    if result.get("isSuccess") and result.get("data"):
        items = result["data"].get("items", result["data"]) if isinstance(result["data"], dict) else result["data"]
        context["giang_vien_list"] = items[:5] if isinstance(items, list) else []
        logger.info(f"✅ Got {len(context.get('giang_vien_list', []))} giảng viên")
    
    return context


# ============================================================================
# PHASE 1: TIỀN GHI DANH - PDT Setup & TLK/TK/PDT Proposals
# ============================================================================

def phase_1_tien_ghi_danh(context: Dict) -> Dict:
    """Phase 1: Setup phases, đề xuất học phần flow"""
    logger.info("\n" + "="*60)
    logger.info("PHASE 1: TIỀN GHI DANH")
    logger.info("="*60)
    
    token_pdt = get_token("pdt")
    hoc_ky = context.get("hoc_ky", {})
    hoc_ky_id = hoc_ky.get("id")
    
    if not hoc_ky_id:
        logger.error("❌ Không có hoc_ky_id")
        return context
    
    # Calculate phase dates (within semester bounds)
    today = datetime.now()
    semester_start = today - timedelta(days=7)  # Assume semester started 1 week ago
    semester_end = today + timedelta(days=120)  # Assume semester ends in 4 months
    
    # Update học kỳ dates if needed
    result = api_call("PATCH", "hoc-ky/dates", {
        "hocKyId": hoc_ky_id,
        "ngayBatDau": semester_start.strftime("%Y-%m-%d"),
        "ngayKetThuc": semester_end.strftime("%Y-%m-%d")
    }, token=token_pdt)
    logger.info(f"Updated hoc ky dates: {result.get('isSuccess')}")
    
    # Phase dates (contiguous, within semester)
    phase_dates = []
    current = semester_start
    
    # Tiền ghi danh: 2 weeks
    phase_dates.append(("de_xuat_phe_duyet", current, current + timedelta(weeks=2)))
    current += timedelta(weeks=2)
    
    # Ghi danh: 2 weeks
    phase_dates.append(("ghi_danh", current, current + timedelta(weeks=2)))
    current += timedelta(weeks=2)
    
    # Sắp xếp TKB: 3 weeks
    phase_dates.append(("sap_xep_tkb", current, current + timedelta(weeks=3)))
    current += timedelta(weeks=3)
    
    # Đăng ký HP: 2 weeks
    phase_dates.append(("dang_ky_hoc_phan", current, current + timedelta(weeks=2)))
    current += timedelta(weeks=2)
    
    # Bình thường: rest
    phase_dates.append(("binh_thuong", current, semester_end))
    
    # Create phases via bulk API
    phases_payload = []
    for phase, start, end in phase_dates:
        phases_payload.append({
            "phase": phase,
            "startAt": start.strftime("%Y-%m-%dT%H:%M:%S"),
            "endAt": end.strftime("%Y-%m-%dT%H:%M:%S")
        })
    
    result = api_call("POST", "pdt/quan-ly-hoc-ky/ky-phase/bulk", {
        "hocKyId": hoc_ky_id,
        "hocKyStartAt": semester_start.strftime("%Y-%m-%dT%H:%M:%S"),
        "hocKyEndAt": semester_end.strftime("%Y-%m-%dT%H:%M:%S"),
        "phases": phases_payload
    }, token=token_pdt)
    logger.info(f"Created phases: {result.get('isSuccess')}")
    
    # Set đợt ghi danh cho toàn trường
    ghi_danh_start = phase_dates[1][1]  # ghi_danh start
    ghi_danh_end = phase_dates[1][2]    # ghi_danh end
    
    result = api_call("POST", "pdt/dot-ghi-danh/update", {
        "hocKyId": hoc_ky_id,
        "isToanTruong": True,
        "thoiGianBatDau": ghi_danh_start.strftime("%Y-%m-%dT%H:%M:%S"),
        "thoiGianKetThuc": ghi_danh_end.strftime("%Y-%m-%dT%H:%M:%S")
    }, token=token_pdt)
    logger.info(f"Set đợt ghi danh toàn trường: {result.get('isSuccess')}")
    
    # Set đợt đăng ký riêng cho khoa CNTT
    dang_ky_start = phase_dates[3][1]  # dang_ky_hoc_phan start
    dang_ky_end = phase_dates[3][2]    # dang_ky_hoc_phan end
    khoa_cntt = context.get("khoa_cntt", {})
    
    if khoa_cntt:
        result = api_call("PUT", "pdt/dot-dang-ky", {
            "hocKyId": hoc_ky_id,
            "isToanTruong": False,
            "dotTheoKhoa": [{
                "khoaId": khoa_cntt.get("id"),
                "thoiGianBatDau": dang_ky_start.strftime("%Y-%m-%dT%H:%M:%S"),
                "thoiGianKetThuc": dang_ky_end.strftime("%Y-%m-%dT%H:%M:%S"),
                "gioiHanTinChi": 25
            }]
        }, token=token_pdt)
        logger.info(f"Set đợt đăng ký cho khoa CNTT: {result.get('isSuccess')}")
    
    # Toggle phase to tiền ghi danh
    result = api_call("PATCH", "pdt/ky-phase/toggle", {
        "hocKyId": hoc_ky_id,
        "phase": "de_xuat_phe_duyet"
    }, token=token_pdt)
    logger.info(f"Toggle tiền ghi danh: {result.get('isSuccess')}")
    
    # ----- TLK: Tạo 3 đề xuất học phần -----
    logger.info("\n--- TLK: Tạo đề xuất học phần ---")
    token_tlk = get_token("tlk")
    
    mon_hoc_list = context.get("mon_hoc_list", [])
    giang_vien_list = context.get("giang_vien_list", [])
    de_xuat_ids = []
    
    for i in range(min(3, len(mon_hoc_list))):
        mon = mon_hoc_list[i]
        gv = giang_vien_list[i % len(giang_vien_list)] if giang_vien_list else None
        
        result = api_call("POST", "tk/de-xuat", {
            "monHocId": mon.get("id"),
            "soLopDuKien": 1,
            "giangVienId": gv.get("id") if gv else None,
            "hocKyId": hoc_ky_id,
            "ghiChu": f"Đề xuất test #{i+1}"
        }, token=token_tlk)
        
        if result.get("isSuccess") and result.get("data"):
            de_xuat_ids.append(result["data"].get("id"))
            logger.info(f"✅ Tạo đề xuất #{i+1}: {mon.get('tenMon')}")
        else:
            logger.warning(f"⚠️ Không tạo được đề xuất #{i+1}")
    
    context["de_xuat_ids"] = de_xuat_ids
    
    # ----- TK: Duyệt 2, từ chối 1 -----
    logger.info("\n--- TK: Duyệt/từ chối đề xuất ---")
    token_tk = get_token("tk")
    
    # Get danh sách đề xuất chờ duyệt
    result = api_call("GET", "tk/de-xuat", token=token_tk)
    if result.get("isSuccess") and result.get("data"):
        pending = [d for d in result["data"] if d.get("trangThai") == "cho_duyet"]
        
        for i, dx in enumerate(pending[:3]):
            if i < 2:  # Duyệt 2 đầu
                result = api_call("PATCH", "tk/de-xuat/duyet", {
                    "id": dx.get("id")
                }, token=token_tk)
                logger.info(f"TK duyệt đề xuất {dx.get('id')[:8]}...: {result.get('isSuccess')}")
            else:  # Từ chối 1
                result = api_call("PATCH", "tk/de-xuat/tu-choi", {
                    "id": dx.get("id")
                }, token=token_tk)
                logger.info(f"TK từ chối đề xuất {dx.get('id')[:8]}...: {result.get('isSuccess')}")
    
    # ----- PDT: Duyệt 1, từ chối 1 -----
    logger.info("\n--- PDT: Duyệt/từ chối đề xuất đã qua TK ---")
    
    result = api_call("GET", "pdt/de-xuat-hoc-phan", token=token_pdt)
    if result.get("isSuccess") and result.get("data"):
        pending = [d for d in result["data"] if d.get("trangThai") == "da_duyet_tk"]
        
        for i, dx in enumerate(pending[:2]):
            if i == 0:  # Duyệt 1
                result = api_call("PATCH", "pdt/de-xuat-hoc-phan/duyet", {
                    "id": dx.get("id")
                }, token=token_pdt)
                logger.info(f"PDT duyệt đề xuất {dx.get('id')[:8]}...: {result.get('isSuccess')}")
                context["de_xuat_duyet_pdt"] = dx
            else:  # Từ chối 1
                result = api_call("PATCH", "pdt/de-xuat-hoc-phan/tu-choi", {
                    "id": dx.get("id")
                }, token=token_pdt)
                logger.info(f"PDT từ chối đề xuất {dx.get('id')[:8]}...: {result.get('isSuccess')}")
    
    return context


# ============================================================================
# PHASE 2: GHI DANH
# ============================================================================

def phase_2_ghi_danh(context: Dict) -> Dict:
    """Phase 2: Ghi danh flow for sinh viên"""
    logger.info("\n" + "="*60)
    logger.info("PHASE 2: GHI DANH")
    logger.info("="*60)
    
    token_pdt = get_token("pdt")
    token_sv = get_token("sinh_vien")
    hoc_ky_id = context.get("hoc_ky", {}).get("id")
    
    # Toggle phase to ghi_danh
    result = api_call("PATCH", "pdt/ky-phase/toggle", {
        "hocKyId": hoc_ky_id,
        "phase": "ghi_danh"
    }, token=token_pdt)
    logger.info(f"Toggle ghi danh: {result.get('isSuccess')}")
    
    # SV: Get danh sách môn ghi danh
    result = api_call("GET", "sv/mon-hoc-ghi-danh", token=token_sv)
    mon_ghi_danh = []
    if result.get("isSuccess") and result.get("data"):
        mon_ghi_danh = result["data"]
        logger.info(f"✅ Có {len(mon_ghi_danh)} môn có thể ghi danh")
    
    if not mon_ghi_danh:
        logger.warning("⚠️ Không có môn để ghi danh")
        return context
    
    # Ghi danh môn đầu
    first_mon = mon_ghi_danh[0]
    hoc_phan_id = first_mon.get("id") or first_mon.get("hocPhanId")
    
    result = api_call("POST", "sv/ghi-danh", {
        "hocPhanId": hoc_phan_id
    }, token=token_sv)
    logger.info(f"Ghi danh: {result.get('isSuccess')}")
    ghi_danh_id = result.get("data", {}).get("id") if result.get("isSuccess") else None
    
    # Get danh sách đã ghi danh
    result = api_call("GET", "sv/ghi-danh/my", token=token_sv)
    logger.info(f"Get ghi danh của tôi: {result.get('isSuccess')}")
    
    # Hủy ghi danh
    if ghi_danh_id:
        result = api_call("DELETE", f"sv/ghi-danh/{ghi_danh_id}", token=token_sv)
        logger.info(f"Hủy ghi danh: {result.get('isSuccess')}")
    
    # Ghi danh lại
    result = api_call("POST", "sv/ghi-danh", {
        "hocPhanId": hoc_phan_id
    }, token=token_sv)
    logger.info(f"Ghi danh lại: {result.get('isSuccess')}")
    
    context["ghi_danh_hoc_phan_id"] = hoc_phan_id
    
    return context


# ============================================================================
# PHASE 3: SẮP XẾP TKB
# ============================================================================

def phase_3_sap_xep_tkb(context: Dict) -> Dict:
    """Phase 3: Sắp xếp TKB - PDT gán phòng, TLK tạo TKB"""
    logger.info("\n" + "="*60)
    logger.info("PHASE 3: SẮP XẾP TKB")
    logger.info("="*60)
    
    token_pdt = get_token("pdt")
    token_tlk = get_token("tlk")
    hoc_ky_id = context.get("hoc_ky", {}).get("id")
    khoa_cntt = context.get("khoa_cntt", {})
    
    # Toggle phase to sap_xep_tkb
    result = api_call("PATCH", "pdt/ky-phase/toggle", {
        "hocKyId": hoc_ky_id,
        "phase": "sap_xep_tkb"
    }, token=token_pdt)
    logger.info(f"Toggle sắp xếp TKB: {result.get('isSuccess')}")
    
    # PDT: Get phòng available
    result = api_call("GET", "pdt/phong-hoc/available", token=token_pdt)
    phong_list = []
    if result.get("isSuccess") and result.get("data"):
        phong_list = result["data"]
        logger.info(f"✅ Có {len(phong_list)} phòng available")
    
    if not phong_list or not khoa_cntt:
        logger.warning("⚠️ Không có phòng hoặc không có khoa CNTT")
        return context
    
    # Gán 1 phòng (test single)
    result = api_call("POST", "pdt/phong-hoc/assign", {
        "khoaId": khoa_cntt.get("id"),
        "phongId": phong_list[0].get("id")
    }, token=token_pdt)
    logger.info(f"Gán 1 phòng: {result.get('isSuccess')}")
    
    # Gán 3 phòng (test array) - if available
    if len(phong_list) >= 4:
        result = api_call("POST", "pdt/phong-hoc/assign", {
            "khoaId": khoa_cntt.get("id"),
            "phongId": [p.get("id") for p in phong_list[1:4]]
        }, token=token_pdt)
        logger.info(f"Gán 3 phòng (array): {result.get('isSuccess')}")
    
    # Get phòng của khoa
    result = api_call("GET", f"pdt/phong-hoc/khoa/{khoa_cntt.get('id')}", token=token_pdt)
    phong_khoa = result.get("data", []) if result.get("isSuccess") else []
    logger.info(f"Khoa CNTT có {len(phong_khoa)} phòng")
    
    # Hủy 1 phòng
    if phong_khoa:
        result = api_call("POST", "pdt/phong-hoc/unassign", {
            "khoaId": khoa_cntt.get("id"),
            "phongId": phong_khoa[0].get("id")
        }, token=token_pdt)
        logger.info(f"Hủy 1 phòng: {result.get('isSuccess')}")
    
    # ----- TLK: Tạo TKB -----
    logger.info("\n--- TLK: Tạo thời khóa biểu ---")
    
    # Get lớp học phần
    result = api_call("GET", f"tk/lop-hoc-phan?hocKyId={hoc_ky_id}", token=token_tlk)
    lop_list = []
    if result.get("isSuccess") and result.get("data"):
        lop_list = result["data"]
        logger.info(f"✅ Có {len(lop_list)} lớp học phần")
    
    if not lop_list:
        logger.warning("⚠️ Không có lớp học phần")
        return context
    
    lop = lop_list[0]
    lop_id = lop.get("id")
    context["lop_hoc_phan_id"] = lop_id
    
    # Refresh phong_khoa after unassign
    result = api_call("GET", f"pdt/phong-hoc/khoa/{khoa_cntt.get('id')}", token=token_pdt)
    phong_khoa = result.get("data", []) if result.get("isSuccess") else []
    
    if phong_khoa:
        # Tạo 2 buổi học
        tkb_data = {
            "lopHocPhanId": lop_id,
            "hocKyId": hoc_ky_id,
            "lichHoc": [
                {
                    "thu": 2,  # Thứ 2
                    "tietBatDau": 1,
                    "tietKetThuc": 3,
                    "phongId": phong_khoa[0].get("id"),
                    "loaiBuoi": "LT"
                },
                {
                    "thu": 4,  # Thứ 4
                    "tietBatDau": 1,
                    "tietKetThuc": 3,
                    "phongId": phong_khoa[0].get("id"),
                    "loaiBuoi": "TH"
                }
            ]
        }
        
        result = api_call("POST", "tk/tkb", tkb_data, token=token_tlk)
        logger.info(f"Tạo TKB (2 buổi): {result.get('isSuccess')}")
    
    return context


# ============================================================================
# PHASE 4: ĐĂNG KÝ HỌC PHẦN
# ============================================================================

def phase_4_dang_ky_hoc_phan(context: Dict) -> Dict:
    """Phase 4: Đăng ký học phần for sinh viên"""
    logger.info("\n" + "="*60)
    logger.info("PHASE 4: ĐĂNG KÝ HỌC PHẦN")
    logger.info("="*60)
    
    token_pdt = get_token("pdt")
    token_sv = get_token("sinh_vien")
    hoc_ky_id = context.get("hoc_ky", {}).get("id")
    
    # Toggle phase to dang_ky_hoc_phan
    result = api_call("PATCH", "pdt/ky-phase/toggle", {
        "hocKyId": hoc_ky_id,
        "phase": "dang_ky_hoc_phan"
    }, token=token_pdt)
    logger.info(f"Toggle đăng ký HP: {result.get('isSuccess')}")
    
    # SV: Get danh sách lớp HP có thể đăng ký
    result = api_call("GET", f"sv/lop-hoc-phan?hocKyId={hoc_ky_id}", token=token_sv)
    lop_list = []
    if result.get("isSuccess") and result.get("data"):
        lop_list = result["data"]
        logger.info(f"✅ Có {len(lop_list)} lớp HP có thể đăng ký")
    
    if not lop_list:
        logger.warning("⚠️ Không có lớp HP để đăng ký")
        return context
    
    lop = lop_list[0]
    lop_id = lop.get("id")
    
    # Đăng ký
    result = api_call("POST", "sv/dang-ky-hoc-phan", {
        "lopHocPhanId": lop_id
    }, token=token_sv)
    logger.info(f"Đăng ký HP: {result.get('isSuccess')}")
    dang_ky_id = result.get("data", {}).get("id") if result.get("isSuccess") else None
    
    # Get đăng ký của tôi
    result = api_call("GET", "sv/dang-ky-hoc-phan/my", token=token_sv)
    logger.info(f"Get đăng ký của tôi: {result.get('isSuccess')}")
    
    # Hủy đăng ký
    if dang_ky_id:
        result = api_call("POST", "sv/huy-dang-ky", {
            "dangKyId": dang_ky_id
        }, token=token_sv)
        logger.info(f"Hủy đăng ký: {result.get('isSuccess')}")
    
    # Đăng ký lại
    result = api_call("POST", "sv/dang-ky-hoc-phan", {
        "lopHocPhanId": lop_id
    }, token=token_sv)
    logger.info(f"Đăng ký lại: {result.get('isSuccess')}")
    
    # Check lịch sử đăng ký
    result = api_call("GET", f"sv/lich-su-dang-ky?hoc_ky_id={hoc_ky_id}", token=token_sv)
    if result.get("isSuccess"):
        count = len(result.get("data", []))
        logger.info(f"✅ Lịch sử đăng ký: {count} records")
    
    # Check tra cứu học phần
    result = api_call("GET", f"sv/tra-cuu-hoc-phan?hocKyId={hoc_ky_id}", token=token_sv)
    logger.info(f"Tra cứu học phần: {result.get('isSuccess')}")
    
    return context


# ============================================================================
# PHASE 5: BÌNH THƯỜNG & HỌC PHÍ
# ============================================================================

def phase_5_binh_thuong_hoc_phi(context: Dict) -> Dict:
    """Phase 5: Bình thường - Tạo chính sách tín chỉ và tính học phí"""
    logger.info("\n" + "="*60)
    logger.info("PHASE 5: BÌNH THƯỜNG & HỌC PHÍ")
    logger.info("="*60)
    
    token_pdt = get_token("pdt")
    hoc_ky_id = context.get("hoc_ky", {}).get("id")
    khoa_cntt = context.get("khoa_cntt", {})
    
    # Toggle phase to binh_thuong
    result = api_call("PATCH", "pdt/ky-phase/toggle", {
        "hocKyId": hoc_ky_id,
        "phase": "binh_thuong"
    }, token=token_pdt)
    logger.info(f"Toggle bình thường: {result.get('isSuccess')}")
    
    if not khoa_cntt:
        logger.warning("⚠️ Không có khoa CNTT")
        return context
    
    # Get ngành của khoa CNTT
    result = api_call("GET", "dm/nganh", token=token_pdt)
    nganh_cntt = None
    if result.get("isSuccess") and result.get("data"):
        for nganh in result["data"]:
            if nganh.get("khoaId") == khoa_cntt.get("id"):
                nganh_cntt = nganh
                break
    
    # Tạo chính sách tín chỉ cho khoa CNTT
    if nganh_cntt:
        result = api_call("POST", "pdt/chinh-sach-tin-chi", {
            "hocKyId": hoc_ky_id,
            "khoaId": khoa_cntt.get("id"),
            "nganhId": nganh_cntt.get("id"),
            "phiMoiTinChi": 700000  # 700k/tín chỉ
        }, token=token_pdt)
        logger.info(f"Tạo chính sách tín chỉ 700k: {result.get('isSuccess')}")
    else:
        logger.warning("⚠️ Không tìm thấy ngành của khoa CNTT")
    
    # Tính học phí hàng loạt
    result = api_call("POST", "pdt/hoc-phi/tinh-toan-hang-loat", {
        "hoc_ky_id": hoc_ky_id
    }, token=token_pdt)
    logger.info(f"Tính học phí hàng loạt: {result.get('isSuccess')}")
    if result.get("isSuccess") and result.get("data"):
        logger.info(f"✅ Đã tính học phí cho {result['data'].get('count', 0)} sinh viên")
    
    return context


# ============================================================================
# MAIN
# ============================================================================

def run_e2e_test():
    """Run complete E2E test"""
    logger.info("="*60)
    logger.info("🚀 STARTING E2E TEST")
    logger.info("="*60)
    
    try:
        # Phase 0: Setup
        context = phase_0_setup()
        
        if not context.get("hoc_ky"):
            logger.error("❌ Cannot proceed without học kỳ")
            return
        
        # Phase 1: Tiền ghi danh
        context = phase_1_tien_ghi_danh(context)
        
        # Phase 2: Ghi danh
        context = phase_2_ghi_danh(context)
        
        # Phase 3: Sắp xếp TKB
        context = phase_3_sap_xep_tkb(context)
        
        # Phase 4: Đăng ký HP
        context = phase_4_dang_ky_hoc_phan(context)
        
        # Phase 5: Bình thường & Học phí
        context = phase_5_binh_thuong_hoc_phi(context)
        
        logger.info("\n" + "="*60)
        logger.info("🎉 E2E TEST COMPLETED!")
        logger.info("="*60)
        
    except Exception as e:
        logger.exception(f"❌ E2E Test failed: {e}")


if __name__ == "__main__":
    run_e2e_test()
