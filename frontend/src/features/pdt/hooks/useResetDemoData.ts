import { useState } from "react";
import { pdtApi } from "../api/pdtApi";
import type { ServiceResult } from "../../common/ServiceResult";

interface ResetDemoDataResult {
    clearedTables: string[];
    errors: string[];
    mongoCleared: boolean;
    totalCleared: number;
}

/**
 * Hook to reset demo data (PDT only)
 * Clears all test/demo data while preserving master data
 */
export const useResetDemoData = () => {
    const [loading, setLoading] = useState(false);

    const resetData = async (): Promise<ServiceResult<ResetDemoDataResult>> => {
        setLoading(true);
        try {
            const result = await pdtApi.resetDemoData();
            return result;
        } catch (error: any) {
            return {
                isSuccess: false,
                message: error.message || "Lỗi khi reset demo data",
            };
        } finally {
            setLoading(false);
        }
    };

    return { resetData, loading };
};
