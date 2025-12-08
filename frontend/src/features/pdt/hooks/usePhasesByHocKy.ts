import { useState, useEffect } from "react";
import { pdtApi } from "../api/pdtApi";
import type { PhasesByHocKyDTO } from "../types/pdtTypes";

/**
 * Hook lấy tất cả phases của 1 học kỳ
 * @param hocKyId - ID học kỳ cần query phases
 */
export const usePhasesByHocKy = (hocKyId: string | null) => {
    const [data, setData] = useState<PhasesByHocKyDTO | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {

        if (!hocKyId) {
            setData(null);
            return;
        }

        const fetchData = async () => {
            setLoading(true);
            setError(null);

            try {
                const result = await pdtApi.getPhasesByHocKy(hocKyId);


                if (result.isSuccess && result.data) {
                    setData(result.data);
                } else {
                    setError(result.message || "Không thể lấy phases");
                    setData(null);
                }
            } catch (err) {
                const errorMessage =
                    err instanceof Error ? err.message : "Lỗi không xác định";
                setError(errorMessage);
                setData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [hocKyId]); // ✅ Re-fetch khi hocKyId thay đổi

    return { data, loading, error };
};