export interface TuChoiDeXuatHocPhanRequest {
    id: string;
}

export interface HocKyHienHanhDTO {
    id: string;
    tenHocKy: string;
    maHocKy: string;
    nienKhoa: {
        id: string;
        tenNienKhoa: string;
    };
    ngayBatDau?: Date;
    ngayKetThuc?: Date;
}

export interface HocKyItemDTO {
    id: string;
    tenHocKy: string;
    maHocKy: string;
    ngayBatDau?: Date;
    ngayKetThuc?: Date;
}

export interface HocKyNienKhoaDTO {
    nienKhoaId: string;
    tenNienKhoa: string;
    hocKy: HocKyItemDTO[];
}
export interface NganhDTO {
    id: string;
    ten_nganh: string;
    khoa_id: string;
}

// Alias for backward compatibility - use HocKyItemDTO structure
export type HocKyDTO = HocKyItemDTO;
