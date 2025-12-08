import { fetchJSON } from "../../../utils/fetchJSON";
import type { ServiceResult } from "../../common/ServiceResult";
import api from "../../../utils/api";

// Types
export interface GVLopHocPhanDTO {
    id: string;
    ma_lop: string;
    so_luong_hien_tai: number | null;
    so_luong_toi_da: number | null;
    hoc_phan: {
        ten_hoc_phan: string;
        mon_hoc: {
            ma_mon: string;
            ten_mon: string;
            so_tin_chi: number;
        };
    };
}

export interface GVLopHocPhanDetailDTO {
    id: string;
    ma_lop: string;
    hoc_phan: {
        ten_hoc_phan: string;
        mon_hoc: {
            ma_mon: string;
            ten_mon: string;
        };
    };
}

export interface GVStudentDTO {
    id: string;
    mssv: string;
    hoTen: string;
    lop: string | null;
    email: string;
}

export interface GVDocumentDTO {
    id: string;
    ten_tai_lieu: string;
    file_path: string;
    file_type: string;
    created_at?: string;
}

export interface GVGradeDTO {
    sinh_vien_id: string;
    diem_so?: number;
}

export interface CreateDocumentRequest {
    ten_tai_lieu: string;
    file_path: string;
}

export interface UpsertGradesRequest {
    items: {
        sinh_vien_id: string;
        diem_so: number;
    }[];
}

export interface UploadTaiLieuResponse {
    id: string;
    tenTaiLieu: string;
    fileType: string;
    fileUrl: string;
}

export const gvLopHocPhanAPI = {
    /**
     * Lấy danh sách lớp học phần của GV
     */
    getMyLopHocPhan: async (): Promise<ServiceResult<GVLopHocPhanDTO[]>> => {
        return await fetchJSON("gv/lop-hoc-phan");
    },

    /**
     * Lấy chi tiết lớp học phần
     */
    getLopHocPhanDetail: async (
        lhpId: string
    ): Promise<ServiceResult<GVLopHocPhanDetailDTO>> => {
        return await fetchJSON(`gv/lop-hoc-phan/${lhpId}`);
    },

    /**
     * Lấy danh sách sinh viên của lớp
     */
    getStudents: async (lhpId: string): Promise<ServiceResult<GVStudentDTO[]>> => {
        return await fetchJSON(`gv/lop-hoc-phan/${lhpId}/sinh-vien`);
    },

    /**
     * Lấy danh sách tài liệu
     */
    getDocuments: async (lhpId: string): Promise<ServiceResult<GVDocumentDTO[]>> => {
        return await fetchJSON(`gv/lop-hoc-phan/${lhpId}/tai-lieu`);
    },

    /**
     * Tạo tài liệu mới
     */
    createDocument: async (
        lhpId: string,
        data: CreateDocumentRequest
    ): Promise<ServiceResult<GVDocumentDTO>> => {
        return await fetchJSON(`gv/lop-hoc-phan/${lhpId}/tai-lieu`, {
            method: "POST",
            body: data,
        });
    },

    /**
     * Lấy điểm của sinh viên
     */
    getGrades: async (lhpId: string): Promise<ServiceResult<GVGradeDTO[]>> => {
        return await fetchJSON(`gv/lop-hoc-phan/${lhpId}/diem`);
    },

    /**
     * Cập nhật điểm sinh viên
     */
    upsertGrades: async (
        lhpId: string,
        data: UpsertGradesRequest
    ): Promise<ServiceResult<null>> => {
        return await fetchJSON(`gv/lop-hoc-phan/${lhpId}/diem`, {
            method: "PUT",
            body: data,
        });
    },

    /**
     * Download file directly (backend streams from S3)
     * @returns Blob for file download
     */
    downloadTaiLieu: async (
        lhpId: string,
        docId: string
    ): Promise<Blob | null> => {
        try {
            const response = await api.get(
                `gv/lop-hoc-phan/${lhpId}/tai-lieu/${docId}/download`,
                {
                    responseType: "blob",
                }
            );

            const blob = response.data;

            if (!blob.type || blob.type === "application/octet-stream") {
                console.warn("Backend returned wrong MIME type, fixing...");

                const contentDisposition = response.headers["content-disposition"];
                let fileName = "";

                if (contentDisposition) {
                    const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                    if (match && match[1]) {
                        fileName = match[1].replace(/['"]/g, "");
                    }
                }


                let correctType = "application/octet-stream";

                if (fileName.toLowerCase().endsWith(".pdf")) {
                    correctType = "application/pdf";
                } else if (fileName.toLowerCase().endsWith(".doc")) {
                    correctType = "application/msword";
                } else if (fileName.toLowerCase().endsWith(".docx")) {
                    correctType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
                } else if (fileName.toLowerCase().endsWith(".jpg") || fileName.toLowerCase().endsWith(".jpeg")) {
                    correctType = "image/jpeg";
                } else if (fileName.toLowerCase().endsWith(".png")) {
                    correctType = "image/png";
                } else if (fileName.toLowerCase().endsWith(".txt")) {
                    correctType = "text/plain";
                }


                return new Blob([blob], { type: correctType });
            }

            return blob;
        } catch (error) {
            console.error("Error downloading file:", error);
            return null;
        }
    },

    /**
     * Get file URL for preview (backend returns blob URL)
     */
    getPreviewUrl: async (
        lhpId: string,
        docId: string
    ): Promise<string | null> => {
        try {
            const blob = await gvLopHocPhanAPI.downloadTaiLieu(lhpId, docId);
            if (!blob) return null;

            const url = URL.createObjectURL(blob);


            return url;
        } catch (error) {
            return null;
        }
    },

    /**
     * Upload tài liệu lên S3 (multipart/form-data)
     */
    uploadTaiLieu: async (
        lhpId: string,
        file: File,
        tenTaiLieu?: string,
        onProgress?: (percent: number) => void
    ): Promise<ServiceResult<UploadTaiLieuResponse>> => {
        const formData = new FormData();
        formData.append("file", file);
        if (tenTaiLieu) {
            formData.append("ten_tai_lieu", tenTaiLieu);
        }

        try {
            const response = await api.post(
                `gv/lop-hoc-phan/${lhpId}/tai-lieu/upload`,
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                    onUploadProgress: (progressEvent) => {
                        if (progressEvent.total && onProgress) {
                            const percent = Math.round(
                                (progressEvent.loaded * 100) / progressEvent.total
                            );
                            onProgress(percent);
                        }
                    },
                }
            );

            return response.data;
        } catch (error: any) {
            return {
                isSuccess: false,
                message: error.response?.data?.message || "Lỗi upload",
            };
        }
    },

    /**
     * Delete tài liệu
     */
    deleteTaiLieu: async (
        lhpId: string,
        docId: string
    ): Promise<ServiceResult<null>> => {
        return await fetchJSON(`gv/lop-hoc-phan/${lhpId}/tai-lieu/${docId}`, {
            method: "DELETE",
        });
    },
};
