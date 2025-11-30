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
     * Gán phòng cho khoa (PATCH /phong-hoc/assign)
     */
    assignPhongToKhoa: async (
        khoaId: string,
        data: AssignPhongRequest
    ): Promise<ServiceResult<{ count: number }>> => {
        return await fetchJSON(`pdt/phong-hoc/assign`, {
            method: "PATCH",
            body: {
                khoaId,
                ...data,
            },
        });
    },

    /**
     * Xóa phòng khỏi khoa (PATCH /phong-hoc/unassign)
     */
    unassignPhongFromKhoa: async (
        khoaId: string,
        data: UnassignPhongRequest
    ): Promise<ServiceResult<{ count: number }>> => {
        return await fetchJSON(`pdt/phong-hoc/unassign`, {
            method: "PATCH",
            body: {
                khoaId,
                ...data,
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
    getDanhSachNganh: async (
        hocKyId: string,
        khoaId: string
    ): Promise<ServiceResult<NganhDTO[]>> => {
        return await fetchJSON(`dm/nganh/chua-co-chinh-sach?hoc_ky_id=${hocKyId}&khoa_id=${khoaId}`);
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
     * Xóa môn học (PDT)
     */
    deleteMonHoc: async (id: string): Promise<ServiceResult<null>> => {
        return await fetchJSON(`pdt/mon-hoc/${id}`, {
            method: "DELETE",
        });
    },

    /**
     * Lấy danh sách giảng viên (PDT)
     */
    getGiangVien: async (): Promise<ServiceResult<{ items: any[] }>> => {
        return await fetchJSON("pdt/giang-vien");
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
};
