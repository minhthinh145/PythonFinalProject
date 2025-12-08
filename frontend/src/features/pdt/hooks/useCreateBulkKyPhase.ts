import { useState } from "react";
import { pdtApi } from "../api/pdtApi";
import type { CreateBulkKyPhaseRequest } from "../types/pdtTypes";

export const useCreateBulkKyPhase = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const createBulkKyPhase = async (request: CreateBulkKyPhaseRequest) => {
        setLoading(true);
        setError(null);

        try {

            const result = await pdtApi.createBulkKyPhase(request);


            if (result.isSuccess) {
                return {
                    isSuccess: true,
                    message: result.message || "Tạo phases thành công",
                };
            } else {
                setError(result.message || "Không thể tạo phases");
                return {
                    isSuccess: false,
                    message: result.message || "Không thể tạo phases",
                };
            }
        } catch (err: any) {
            console.error("❌ Error creating bulk ky phase:", err);
            const errorMessage = err.message || "Có lỗi xảy ra";
            setError(errorMessage);
            return {
                isSuccess: false,
                message: errorMessage,
            };
        } finally {
            setLoading(false);
        }
    };

    return {
        createBulkKyPhase,
        loading,
        error,
    };
};