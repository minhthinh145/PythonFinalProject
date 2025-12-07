import { fetchJSON } from "../../../utils/fetchJSON";
import api from "../../../utils/api";
import type { ServiceResult } from "../../common/ServiceResult";
import type { TuChoiDeXuatHocPhanRequest } from "../../common/types";
import type {
    CreateBulkKyPhaseRequest,
    SetHocKyHienThanhRequest,
    KyPhaseResponseDTO,
    HocKyDTO,
    DeXuatHocPhanForPDTDTO,
    UpdateTrangThaiByPDTRequest,
    PhasesByHocKyDTO,
    KhoaDTO,
    UpdateDotGhiDanhRequest,
    DotGhiDanhResponseDTO,
    PhongHocDTO,
    AssignPhongRequest,
    UnassignPhongRequest,
    UpdateDotDangKyRequest,
    DotDangKyResponseDTO,
    ChinhSachTinChiDTO,
    CreateChinhSachTinChiRequest,
    NganhDTO,
    UpdateChinhSachTinChiRequest,
    TinhHocPhiHangLoatRequest,
    TinhHocPhiHangLoatResponse,
    BaoCaoTheoNganhResponse,
    BaoCaoTheoKhoaResponse,
    OverviewPayload,
    BaoCaoTaiGVResponse,
} from "../types/pdtTypes";

/**
 * PDT API Service
 */
export const pdtApi = {
    /**
     * Thiết lập học kỳ hiện hành (PDT only)
     */
    setHocKyHienHanh: async (
        data: SetHocKyHienThanhRequest
    ): Promise<ServiceResult<HocKyDTO>> => {
        return await fetchJSON("pdt/quan-ly-hoc-ky/hoc-ky-hien-hanh", {
            method: "POST",
            body: data,
        });
    },

    /**
     * Thiết lập học kỳ hiện tại với ngày bắt đầu/kết thúc (Legacy API)
     */
    setHocKyHienTai: async (
        data: { id_nien_khoa?: string; id_hoc_ky: string; ngay_bat_dau: string; ngay_ket_thuc: string }
    ): Promise<ServiceResult<KyPhaseResponseDTO>> => {
        // Map to the new API format
        return await fetchJSON("hoc-ky/dates", {
            method: "PATCH",
            body: {
                hocKyId: data.id_hoc_ky,
                ngayBatDau: data.ngay_bat_dau,
                ngayKetThuc: data.ngay_ket_thuc,
            },
        });
    },

    /**
     * Bulk upsert phases (PDT only)
     */
    createBulkKyPhase: async (
        data: CreateBulkKyPhaseRequest
    ): Promise<ServiceResult<KyPhaseResponseDTO[]>> => {
        return await fetchJSON("pdt/quan-ly-hoc-ky/ky-phase/bulk", {
            method: "POST",
            body: data,
        });
    },


    /**
     * Lấy tất cả phases theo học kỳ ID (PDT only)
     */
    getPhasesByHocKy: async (hocKyId: string): Promise<ServiceResult<PhasesByHocKyDTO>> => {
        return await fetchJSON(`pdt/quan-ly-hoc-ky/ky-phase/${hocKyId}`, {
            method: "GET",
        });
    },

    /**
     * Lấy danh sách đề xuất học phần cho PDT
     */
    getDeXuatHocPhan: async (): Promise<ServiceResult<DeXuatHocPhanForPDTDTO[]>> => {
        return await fetchJSON("pdt/de-xuat-hoc-phan", {
            method: "GET",
        });
    },

    /**
     * Duyệt đề xuất học phần (PDT)
     */
    duyetDeXuatHocPhan: async (
        data: UpdateTrangThaiByPDTRequest
    ): Promise<ServiceResult<null>> => {
        return await fetchJSON("pdt/de-xuat-hoc-phan/duyet", {
            method: "PATCH",
            body: data,
        });
    },

    /**
     * Từ chối đề xuất học phần (shared endpoint)
     */
    tuChoiDeXuatHocPhan: async (
        data: TuChoiDeXuatHocPhanRequest
    ): Promise<ServiceResult<null>> => {
        return await fetchJSON("pdt/de-xuat-hoc-phan/tu-choi", {
            method: "PATCH",
            body: data,
        });
    },

    /**
     * Lấy danh sách khoa
     */
    getDanhSachKhoa: async (): Promise<ServiceResult<KhoaDTO[]>> => {
        return await fetchJSON("pdt/khoa", {
            method: "GET",
        });
    },

    /**
     * Cập nhật đợt ghi danh theo khoa
     */
    updateDotGhiDanh: async (
        data: UpdateDotGhiDanhRequest
    ): Promise<ServiceResult<DotGhiDanhResponseDTO[]>> => {
        return await fetchJSON("pdt/dot-ghi-danh/update", {
            method: "POST",
            body: data,
        });
    },

    /**
     * Lấy danh sách đợt ghi danh theo học kỳ
     */
    getDotGhiDanhByHocKy: async (
        hocKyId: string
    ): Promise<ServiceResult<DotGhiDanhResponseDTO[]>> => {
        return await fetchJSON(`pdt/dot-dang-ky/${hocKyId}`, {
            method: "GET",
        });
    },

    /**
     * Lấy danh sách phòng học available (chưa được phân)
     */
    getAvailablePhongHoc: async (): Promise<ServiceResult<PhongHocDTO[]>> => {
        return await fetchJSON("pdt/phong-hoc/available", {
            method: "GET",
        });
    },

    /**
     * Lấy danh sách phòng học của khoa
     */
    getPhongHocByKhoa: async (khoaId: string): Promise<ServiceResult<PhongHocDTO[]>> => {
        return await fetchJSON(`pdt/phong-hoc/khoa/${khoaId}`, {
            method: "GET",
        });
    },

    /**
     * Gán phòng cho khoa (POST /phong-hoc/assign)
     * BE support cả single string và array
     */
    assignPhongToKhoa: async (
        khoaId: string,
        phongId: string | string[]
    ): Promise<ServiceResult<{ count: number }>> => {
        return await fetchJSON(`pdt/phong-hoc/assign`, {
            method: "POST",
            body: {
                khoaId,
                phongId,
            },
        });
    },

    /**
     * Xóa phòng khỏi khoa (POST /phong-hoc/unassign)  
     */
    unassignPhongFromKhoa: async (
        khoaId: string,
        phongId: string
    ): Promise<ServiceResult<{ count: number }>> => {
        return await fetchJSON(`pdt/phong-hoc/unassign`, {
            method: "POST",
            body: {
                khoaId,
                phongId,
            },
        });
    },

    /**
     * Lấy danh sách đợt đăng ký học phần theo học kỳ
     */
    getDotDangKyByHocKy: async (hocKyId: string): Promise<ServiceResult<DotDangKyResponseDTO[]>> => {
        return await fetchJSON(`pdt/dot-dang-ky?hoc_ky_id=${hocKyId}`);
    },

    /**
     * Cập nhật/Tạo mới đợt đăng ký học phần
     */
    updateDotDangKy: async (data: UpdateDotDangKyRequest): Promise<ServiceResult<null>> => {
        return await fetchJSON("pdt/dot-dang-ky", {
            method: "PUT",
            body: data,
        });
    },

    /**
     * Lấy danh sách chính sách tín chỉ
     */
    getChinhSachTinChi: async (): Promise<ServiceResult<ChinhSachTinChiDTO[]>> => {
        return await fetchJSON("pdt/chinh-sach-tin-chi");
    },

    /**
     * Tạo chính sách tín chỉ
     */
    createChinhSachTinChi: async (
        data: CreateChinhSachTinChiRequest
    ): Promise<ServiceResult<ChinhSachTinChiDTO>> => {
        return await fetchJSON("pdt/chinh-sach-tin-chi", {
            method: "POST",
            body: data,
        });
    },

    /**
     * Cập nhật phí tín chỉ
     */
    updateChinhSachTinChi: async (
        id: string,
        data: UpdateChinhSachTinChiRequest
    ): Promise<ServiceResult<ChinhSachTinChiDTO>> => {
        return await fetchJSON(`pdt/chinh-sach-tin-chi/${id}`, {
            method: "PUT",
            body: data,
        });
    },

    /**
     * Lấy danh sách ngành chưa có chính sách tín chỉ (REQUIRED hocKyId & khoaId)
     */
    /**
     * Lấy danh sách ngành chưa có chính sách tín chỉ (REQUIRED hocKyId & khoaId)
     */
    getDanhSachNganh: async (
        hocKyId: string,
        khoaId: string
    ): Promise<ServiceResult<NganhDTO[]>> => {
        return await fetchJSON(`dm/nganh/chua-co-chinh-sach?hoc_ky_id=${hocKyId}&khoa_id=${khoaId}`);
    },

    /**
     * Lấy tất cả danh sách ngành (Danh mục)
     */
    getAllNganh: async (): Promise<ServiceResult<NganhDTO[]>> => {
        return await fetchJSON("dm/nganh");
    },

    /**
     * Tính học phí hàng loạt cho học kỳ
     */
    tinhHocPhiHangLoat: async (
        data: TinhHocPhiHangLoatRequest
    ): Promise<ServiceResult<TinhHocPhiHangLoatResponse>> => {
        return await fetchJSON("tuition/calculate-semester", {
            method: "POST",
            body: data,
        });
    },

    /**
     * Lấy thống kê tổng quan
     */
    getBaoCaoOverview: async (params: {
        hoc_ky_id: string;
        khoa_id?: string;
        nganh_id?: string;
    }): Promise<ServiceResult<OverviewPayload>> => {
        const qs = new URLSearchParams();
        qs.set("hoc_ky_id", params.hoc_ky_id);
        if (params.khoa_id) qs.set("khoa_id", params.khoa_id);
        if (params.nganh_id) qs.set("nganh_id", params.nganh_id);

        return await fetchJSON(`bao-cao/overview?${qs.toString()}`);
    },

    /**
     * Lấy thống kê đăng ký theo khoa
     */
    getBaoCaoDangKyTheoKhoa: async (
        hocKyId: string
    ): Promise<ServiceResult<BaoCaoTheoKhoaResponse>> => {
        return await fetchJSON(`bao-cao/dk-theo-khoa?hoc_ky_id=${hocKyId}`);
    },

    /**
     * Lấy thống kê đăng ký theo ngành
     */
    getBaoCaoDangKyTheoNganh: async (params: {
        hocKyId: string;
        khoaId?: string;
    }): Promise<ServiceResult<BaoCaoTheoNganhResponse>> => {
        const url = params.khoaId
            ? `bao-cao/dk-theo-nganh?hoc_ky_id=${params.hocKyId}&khoa_id=${params.khoaId}`
            : `bao-cao/dk-theo-nganh?hoc_ky_id=${params.hocKyId}`;

        return await fetchJSON(url);
    },

    /**
     * Lấy thống kê tải giảng viên
     */
    getBaoCaoTaiGiangVien: async (params: {
        hocKyId: string;
        khoaId?: string;
    }): Promise<ServiceResult<BaoCaoTaiGVResponse>> => {
        const url = params.khoaId
            ? `bao-cao/tai-giang-vien?hoc_ky_id=${params.hocKyId}&khoa_id=${params.khoaId}`
            : `bao-cao/tai-giang-vien?hoc_ky_id=${params.hocKyId}`;

        return await fetchJSON(url);
    },

    /**
     * Lấy danh sách sinh viên (PDT)
     */
    getSinhVien: async (): Promise<ServiceResult<{ items: any[] }>> => {
        return await fetchJSON("pdt/sinh-vien");
    },

    /**
     * Xóa sinh viên (PDT)
     */
    deleteSinhVien: async (id: string): Promise<ServiceResult<null>> => {
        return await fetchJSON(`pdt/sinh-vien/${id}`, {
            method: "DELETE",
        });
    },

    /**
     * Lấy danh sách môn học (PDT)
     */
    getMonHoc: async (): Promise<ServiceResult<{ items: any[] }>> => {
        return await fetchJSON("pdt/mon-hoc?page=1&pageSize=10000");
    },

    /**
     * Lấy chi tiết môn học theo ID
     */
    getMonHocById: async (id: string): Promise<ServiceResult<any>> => {
        return await fetchJSON(`pdt/mon-hoc/${id}`);
    },

    /**
     * Thêm môn học mới (PDT)
     */
    createMonHoc: async (data: {
        ma_mon: string;
        ten_mon: string;
        so_tin_chi: number;
        khoa_id: string;
        loai_mon?: string;
        la_mon_chung?: boolean;
        thu_tu_hoc?: number;
        nganh_ids?: string[];
        dieu_kien?: { mon_lien_quan_id: string; loai: string; bat_buoc: boolean }[];
    }): Promise<ServiceResult<any>> => {
        return await fetchJSON("pdt/mon-hoc", {
            method: "POST",
            body: data,
        });
    },

    /**
     * Cập nhật môn học (PDT)
     */
    updateMonHoc: async (id: string, data: {
        ma_mon?: string;
        ten_mon?: string;
        so_tin_chi?: number;
        khoa_id?: string;
        loai_mon?: string;
        la_mon_chung?: boolean;
        thu_tu_hoc?: number;
        nganh_ids?: string[] | null;
        dieu_kien?: { mon_lien_quan_id: string; loai: string; bat_buoc: boolean }[] | null;
    }): Promise<ServiceResult<any>> => {
        return await fetchJSON(`pdt/mon-hoc/${id}`, {
            method: "PUT",
            body: data,
        });
    },

    /**
     * Xóa môn học (PDT)
     */
    deleteMonHoc: async (id: string): Promise<ServiceResult<null>> => {
        return await fetchJSON(`pdt/mon-hoc/${id}`, {
            method: "DELETE",
        });
    },

    /**
     * Lấy danh sách ngành (Danh mục) - tất cả
     */
    getDanhMucNganh: async (): Promise<ServiceResult<any[]>> => {
        return await fetchJSON("dm/nganh");
    },

    /**
     * Lấy danh sách giảng viên (PDT)
     */
    getGiangVien: async (): Promise<ServiceResult<{ items: any[] }>> => {
        return await fetchJSON("pdt/giang-vien");
    },

    /**
     * Lấy chi tiết giảng viên theo ID
     */
    getGiangVienById: async (id: string): Promise<ServiceResult<any>> => {
        return await fetchJSON(`pdt/giang-vien/${id}`);
    },

    /**
     * Thêm giảng viên mới (PDT)
     */
    createGiangVien: async (data: {
        ten_dang_nhap: string;
        mat_khau: string;
        ho_ten: string;
        khoa_id: string;
        trinh_do?: string;
        chuyen_mon?: string;
        kinh_nghiem_giang_day?: number;
    }): Promise<ServiceResult<any>> => {
        return await fetchJSON("pdt/giang-vien", {
            method: "POST",
            body: data,
        });
    },

    /**
     * Cập nhật giảng viên (PDT)
     */
    updateGiangVien: async (id: string, data: {
        ho_ten?: string;
        mat_khau?: string;
        khoa_id?: string;
        trinh_do?: string;
        chuyen_mon?: string;
        kinh_nghiem_giang_day?: number;
    }): Promise<ServiceResult<any>> => {
        return await fetchJSON(`pdt/giang-vien/${id}`, {
            method: "PUT",
            body: data,
        });
    },

    /**
     * Xóa giảng viên (PDT)
     */
    deleteGiangVien: async (id: string): Promise<ServiceResult<null>> => {
        return await fetchJSON(`pdt/giang-vien/${id}`, {
            method: "DELETE",
        });
    },

    /**
     * Lấy danh sách khoa (Danh mục)
     */
    getDanhMucKhoa: async (): Promise<ServiceResult<any[]>> => {
        return await fetchJSON("dm/khoa");
    },

    /**
     * Export Excel báo cáo
     */
    exportBaoCaoExcel: async (params: {
        hoc_ky_id: string;
        khoa_id?: string;
        nganh_id?: string;
    }): Promise<Blob> => {
        const qs = new URLSearchParams();
        qs.set("hoc_ky_id", params.hoc_ky_id);
        if (params.khoa_id) qs.set("khoa_id", params.khoa_id);
        if (params.nganh_id) qs.set("nganh_id", params.nganh_id);

        const response = await api.get(`bao-cao/export/excel?${qs.toString()}`, {
            responseType: "blob",
        });

        return response.data;
    },

    /**
     * Export PDF báo cáo
     */
    exportBaoCaoPDF: async (data: {
        hoc_ky_id: string;
        khoa_id?: string;
        nganh_id?: string;
        charts: { name: string; dataUrl: string }[];
    }): Promise<Blob> => {
        const response = await api.post(`bao-cao/export/pdf`, data, {
            responseType: "blob",
        });

        return response.data;
    },
    /**
     * Toggle Phase (Demo)
     */
    togglePhase: async (data: { hocKyId?: string; phase: string }): Promise<ServiceResult<{ isEnabled: boolean; phase: string }>> => {
        return await fetchJSON("pdt/ky-phase/toggle", {
            method: "PATCH",
            body: data,
        });
    },

    /**
     * Reset Demo Data - Clears all test/demo data while preserving master data
     * Requires { confirmReset: true } in body
     */
    resetDemoData: async (): Promise<ServiceResult<{
        clearedTables: string[];
        errors: string[];
        mongoCleared: boolean;
        totalCleared: number;
    }>> => {
        return await fetchJSON("pdt/demo/reset-data", {
            method: "POST",
            body: { confirmReset: true },
        });
    },

    /**
     * Delete Chinh Sach Tin Chi (PDT)
     */
    deleteChinhSachTinChi: async (id: string): Promise<ServiceResult<null>> => {
        return await fetchJSON(`pdt/chinh-sach-tin-chi/${id}`, {
            method: "DELETE",
        });
    },
};
