import { useState, useEffect } from "react";
import { commonApi } from "../api/commonApi";
import type { NganhDTO } from "../types";

export const useDanhSachNganh = (khoaId?: string) => {
    const [data, setData] = useState<NganhDTO[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);

            try {
                const result = await commonApi.getDanhSachNganh(khoaId);

                if (result.isSuccess && result.data) {
                    setData(result.data);
                } else {
                    setError(result.message || "Không thể lấy danh sách ngành");
                    setData([]);
                }
            } catch (err) {
                const errorMessage =
                    err instanceof Error ? err.message : "Lỗi không xác định";
                setError(errorMessage);
                setData([]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [khoaId]);

    return { data, loading, error };
};
