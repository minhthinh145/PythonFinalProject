import { useState, useEffect } from "react";
import { pdtApi } from "../api/pdtApi";
import type { NganhDTO } from "../types/pdtTypes";

/**
 * ✅ Hook lấy danh sách ngành (REQUIRED hocKyId & khoaId)
 */
export const useDanhSachNganh = (hocKyId: string, khoaId: string) => {
    const [data, setData] = useState<NganhDTO[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // ✅ Chỉ fetch khi có đủ cả 2 params
        if (!hocKyId || !khoaId) {
            setData([]);
            return;
        }

        const fetchData = async () => {
            setLoading(true);
            try {
                const result = await pdtApi.getDanhSachNganh(hocKyId, khoaId);
                if (result.isSuccess && result.data) {
                    // Map snake_case from API to camelCase for NganhDTO
                    const mapped = result.data.map((n: any) => ({
                        id: n.id,
                        maNganh: n.maNganh || n.ma_nganh,
                        tenNganh: n.tenNganh || n.ten_nganh,
                        khoaId: n.khoaId || n.khoa_id,
                    }));
                    setData(mapped);
                } else {
                    setData([]);
                }
            } catch (error) {
                console.error(error);
                setData([]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [hocKyId, khoaId]);

    return { data, loading };
};
