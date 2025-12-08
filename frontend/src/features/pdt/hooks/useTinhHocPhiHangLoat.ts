import { useState } from "react";
import { pdtApi } from "../api/pdtApi";
import { useModalContext } from "../../../hook/ModalContext";

export const useTinhHocPhiHangLoat = () => {
    const { openNotify } = useModalContext();
    const [loading, setLoading] = useState(false);

    const tinhHocPhi = async (hocKyId: string) => {
        if (!hocKyId) {
            openNotify({
                message: "Vui lòng chọn học kỳ trước khi tính học phí",
                type: "warning",
            });
            return false;
        }

        setLoading(true);

        try {

            const result = await pdtApi.tinhHocPhiHangLoat({ hoc_ky_id: hocKyId });

            if (result.isSuccess && result.data) {
                const { successCount, totalProcessed, failedCount, errors } = result.data;


                // ✅ Show success notification
                openNotify({
                    message: `✅ Tính học phí thành công cho ${successCount}/${totalProcessed} sinh viên`,
                    type: "success",
                });

                // ✅ Show errors if any
                if (failedCount > 0 && errors.length > 0) {
                    const errorMessages = errors
                        .slice(0, 5) // Only show first 5 errors
                        .map((e) => `${e.mssv}: ${e.error}`)
                        .join("\n");

                    openNotify({
                        message: `⚠️ Có ${failedCount} sinh viên lỗi:\n${errorMessages}${errors.length > 5 ? "\n..." : ""
                            }`,
                        type: "warning",
                    });
                }

                return true;
            } else {
                openNotify({
                    message: result.message || "Không thể tính học phí",
                    type: "error",
                });
                return false;
            }
        } catch (error: any) {
            console.error("❌ Error:", error);
            openNotify({
                message: error.message || "Đã xảy ra lỗi khi tính học phí",
                type: "error",
            });
            return false;
        } finally {
            setLoading(false);
        }
    };

    return { tinhHocPhi, loading };
};
