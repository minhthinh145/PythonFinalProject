import { fetchJSON } from "../../../utils/fetchJSON";
import type { ServiceResult } from "../../common/ServiceResult";
import type {
    DeXuatHocPhanRequest,
    DeXuatHocPhanForTroLyKhoaDTO,
    HocPhanForCreateLopDTO,
    PhongHocDTO,
    XepTKBRequest,
    ThoiKhoaBieuMonHocDTO,
    MonHocDTO,
    GiangVienDTO,
    HocKyHienHanhResponse,
} from "../types";

export const tlkAPI = {
    // ============ Học kỳ hiện hành ============
    /**
     * Lấy thông tin học kỳ hiện hành
     */
    getHocKyHienHanh: async (): Promise<ServiceResult<HocKyHienHanhResponse>> => {
        return await fetchJSON("hien-hanh", {
            method: "GET",
        });
    },

    // ============ Môn học theo khoa của TLK ============
    /**
     * Lấy danh sách môn học theo khoa của TLK
     */
    getMonHoc: async (): Promise<ServiceResult<MonHocDTO[]>> => {
        return await fetchJSON("tlk/mon-hoc", {
            method: "GET",
        });
    },

    // ============ Giảng viên theo khoa của TLK ============
    /**
     * Lấy danh sách giảng viên theo khoa của TLK
     * @param monHocId - Optional: filter by mon_hoc_id
     */
    getGiangVien: async (monHocId?: string): Promise<ServiceResult<GiangVienDTO[]>> => {
        const url = monHocId ? `tlk/giang-vien?mon_hoc_id=${monHocId}` : "tlk/giang-vien";
        return await fetchJSON(url, {
            method: "GET",
        });
    },

    // ============ Đề xuất học phần ============
    /**
     * Tạo đề xuất học phần
     */
    createDeXuatHocPhan: async (data: DeXuatHocPhanRequest): Promise<ServiceResult<null>> => {
        return await fetchJSON("tlk/de-xuat-hoc-phan", {
            method: "POST",
            body: data,
        });
    },

    getDeXuatHocPhan: async (): Promise<ServiceResult<DeXuatHocPhanForTroLyKhoaDTO[]>> => {
        return await fetchJSON("tlk/de-xuat-hoc-phan", {
            method: "GET",
        });
    },

    /**
     * COPY từ PDT - Lấy phòng học available
     */
    getAvailablePhongHoc: async (): Promise<ServiceResult<PhongHocDTO[]>> => {
        return await fetchJSON("tlk/phong-hoc/available", {
            method: "GET",
        });
    },

    /**
     * MOVE từ PDT - Lấy học phần để tạo lớp
     */
    getHocPhansForCreateLop: async (hocKyId: string): Promise<ServiceResult<HocPhanForCreateLopDTO[]>> => {
        return await fetchJSON(`tlk/lop-hoc-phan/get-hoc-phan/${hocKyId}`, {
            method: "GET",
        });
    },

    /**
     * Lấy tất cả phòng học của TLK (có thể filter theo khoa)
     */
    getPhongHocByTLK: async (): Promise<ServiceResult<PhongHocDTO[]>> => {
        return await fetchJSON("tlk/phong-hoc", {
            method: "GET",
        });
    },

    /**
     * Lấy TKB đã có của nhiều môn học
     */
    getTKBByMaHocPhans: async (
        maHocPhans: string[],
        hocKyId: string
    ): Promise<ServiceResult<ThoiKhoaBieuMonHocDTO[]>> => {
        return await fetchJSON("tlk/thoi-khoa-bieu/batch", {
            method: "POST",
            body: { maHocPhans, hocKyId },
        });
    },

    /**
     * Xếp thời khóa biểu
     */
    xepThoiKhoaBieu: async (data: XepTKBRequest): Promise<ServiceResult<any>> => {
        return await fetchJSON("tlk/thoi-khoa-bieu", {
            method: "POST",
            body: data,
        });
    },
};