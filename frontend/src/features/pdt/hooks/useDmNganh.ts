import { useState, useEffect } from "react";
import { pdtApi } from "../api/pdtApi";
import type { NganhDTO } from "../types/pdtTypes";

/**
 * Hook lấy danh mục tất cả ngành
 */
export const useDmNganh = () => {
    const [data, setData] = useState<NganhDTO[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const result = await pdtApi.getAllNganh();
                if (result.isSuccess && result.data) {
                    setData(result.data);
                } else {
                    setError(result.message || "Không thể tải danh sách ngành");
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Lỗi tải danh sách ngành");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return { data, loading, error };
};
