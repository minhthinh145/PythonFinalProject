import { useState, useEffect } from "react";
import {
    gvLopHocPhanAPI,
    type GVLopHocPhanDetailDTO,
    type GVStudentDTO,
    type GVDocumentDTO,
    type GVGradeDTO,
} from "../api/gvLopHocPhanAPI";
import { useModalContext } from "../../../hook/ModalContext";

export const useGVLopHocPhanDetail = (lhpId: string) => {
    const { openNotify, openConfirm } = useModalContext();

    const [info, setInfo] = useState<GVLopHocPhanDetailDTO | null>(null);
    const [students, setStudents] = useState<GVStudentDTO[]>([]);
    const [documents, setDocuments] = useState<GVDocumentDTO[]>([]);
    const [grades, setGrades] = useState<Record<string, number | "">>({});

    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});

    // Load info
    const loadInfo = async () => {
        try {
            const result = await gvLopHocPhanAPI.getLopHocPhanDetail(lhpId);
            if (result.isSuccess && result.data) {
                setInfo(result.data);
            }
        } catch (err) {
            console.error("Error loading info:", err);
        }
    };

    const loadStudents = async () => {
        try {
            const result = await gvLopHocPhanAPI.getStudents(lhpId);
            if (result.isSuccess && result.data) {
                setStudents(result.data);
            }
        } catch (err) {
            console.error("Error loading students:", err);
        }
    };

    // Load documents
    const loadDocuments = async () => {
        try {
            const result = await gvLopHocPhanAPI.getDocuments(lhpId);
            if (result.isSuccess && result.data) {
                setDocuments(result.data);
            }
        } catch (err) {
            console.error("Error loading documents:", err);
        }
    };

    const loadGrades = async () => {
        try {
            const result = await gvLopHocPhanAPI.getGrades(lhpId);


            if (result.isSuccess && result.data) {
                const map: Record<string, number | ""> = {};

                if (Array.isArray(result.data)) {
                    // ✅ sinh_vien_id from BE should be UUID
                    result.data.forEach((g) => (map[g.sinh_vien_id] = g.diem_so ?? ""));
                } else {
                    console.warn("⚠️ result.data is not an array:", result.data);
                    const dataArray = (result.data as any)?.rows || [];
                    dataArray.forEach((g: any) => (map[g.sinh_vien_id] = g.diem_so ?? ""));
                }

                setGrades(map);
            } else {
                setGrades({});
            }
        } catch (err) {
            console.error("Error loading grades:", err);
            setGrades({});
        }
    };

    // Upload document
    const uploadDocument = async (ten: string, path: string) => {
        if (!ten || !path) {
            openNotify({ message: "Thiếu tên hoặc đường dẫn", type: "warning" });
            return false;
        }

        const confirmed = await openConfirm({ message: `Đăng tài liệu "${ten}"?` });
        if (!confirmed) return false;

        setSubmitting(true);
        try {
            const result = await gvLopHocPhanAPI.createDocument(lhpId, {
                ten_tai_lieu: ten,
                file_path: path,
            });

            if (result.isSuccess) {
                openNotify({ message: "Đã đăng tài liệu", type: "success" });
                await loadDocuments();
                return true;
            } else {
                openNotify({ message: result.message || "Lỗi đăng tài liệu", type: "error" });
                return false;
            }
        } catch (err) {
            openNotify({ message: "Lỗi kết nối", type: "error" });
            return false;
        } finally {
            setSubmitting(false);
        }
    };

    // Upload multiple files
    const uploadMultipleFiles = async (
        filesWithNames: { file: File; name: string }[]
    ) => {
        if (filesWithNames.length === 0) return;

        const MAX_SIZE = 100 * 1024 * 1024; // 100MB
        const ALLOWED_TYPES = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "video/mp4",
            "image/jpeg",
            "image/png",
            "application/zip",
        ];

        const invalidFiles = filesWithNames.filter(
            (item) =>
                item.file.size > MAX_SIZE || !ALLOWED_TYPES.includes(item.file.type)
        );

        if (invalidFiles.length > 0) {
            openNotify({
                message: `${invalidFiles.length} file không hợp lệ (quá lớn hoặc không đúng định dạng)`,
                type: "error",
            });
            return;
        }

        setSubmitting(true);

        let successCount = 0;

        for (const { file, name } of filesWithNames) {
            const fileId = `${Date.now()}-${Math.random()}`;

            try {
                setUploadProgress((prev) => ({ ...prev, [fileId]: 0 }));

                const result = await gvLopHocPhanAPI.uploadTaiLieu(
                    lhpId,
                    file,
                    name,
                    (percent) => {
                        setUploadProgress((prev) => ({ ...prev, [fileId]: percent }));
                    }
                );

                if (result.isSuccess) {
                    successCount++;
                } else {
                    openNotify({
                        message: `Lỗi upload ${name}: ${result.message}`,
                        type: "error",
                    });
                }
            } catch (err) {
                console.error(`Error uploading ${name}:`, err);
            } finally {
                setUploadProgress((prev) => {
                    const newProgress = { ...prev };
                    delete newProgress[fileId];
                    return newProgress;
                });
            }
        }

        if (successCount > 0) {
            openNotify({
                message: `Đã upload ${successCount}/${filesWithNames.length} file`,
                type: "success",
            });
            await loadDocuments();
        }

        setSubmitting(false);
    };

    // Delete document
    const deleteDocument = async (docId: string) => {
        const confirmed = await openConfirm({
            message: "Xóa tài liệu này?",
            confirmText: "Xóa",
        });

        if (!confirmed) return;

        setSubmitting(true);
        try {
            const result = await gvLopHocPhanAPI.deleteTaiLieu(lhpId, docId);

            if (result.isSuccess) {
                openNotify({ message: "Đã xóa tài liệu", type: "success" });
                await loadDocuments();
            } else {
                openNotify({ message: result.message || "Lỗi xóa", type: "error" });
            }
        } catch (err) {
            openNotify({ message: "Lỗi kết nối", type: "error" });
        } finally {
            setSubmitting(false);
        }
    };

    const saveGrades = async () => {
        const items = Object.entries(grades)
            .filter(([, v]) => v !== "")
            .map(([sinh_vien_id, diem_so]) => ({
                sinh_vien_id,
                diem_so: Number(diem_so),
            }));

        const confirmed = await openConfirm({
            message: "Lưu điểm cho lớp này?",
            confirmText: "Lưu",
        });

        if (!confirmed) return;

        setSubmitting(true);
        try {
            const result = await gvLopHocPhanAPI.upsertGrades(lhpId, { items });

            if (result.isSuccess) {
                openNotify({ message: "Đã lưu điểm", type: "success" });
                await loadGrades();
            } else {
                openNotify({ message: result.message || "Lỗi lưu điểm", type: "error" });
            }
        } catch (err) {
            openNotify({ message: "Lỗi kết nối", type: "error" });
        } finally {
            setSubmitting(false);
        }
    };

    const getDocumentUrl = async (docId: string): Promise<string | null> => {
        try {
            const url = await gvLopHocPhanAPI.getPreviewUrl(lhpId, docId);

            if (url) {
                return url;
            } else {
                openNotify({
                    message: "Không thể tải file",
                    type: "error",
                });
                return null;
            }
        } catch (err) {
            openNotify({ message: "Lỗi kết nối", type: "error" });
            return null;
        }
    };

    // Init load
    useEffect(() => {
        (async () => {
            setLoading(true);
            await Promise.all([loadInfo(), loadStudents(), loadDocuments(), loadGrades()]);
            setLoading(false);
        })();
    }, [lhpId]);

    return {
        info,
        students,
        documents,
        grades,
        loading,
        submitting,
        uploadProgress,
        setGrades,
        uploadMultipleFiles,
        deleteDocument,
        saveGrades,
        getDocumentUrl, // ✅ Export new method
    };
};
