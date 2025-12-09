import { useState, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export interface SinhVienInfoDTO {
    id: string;
    maSoSinhVien: string;
    hoTen: string;
    email: string;
    nganhId?: string;
    tenNganh?: string;
    lop?: string;
    khoaId?: string;
    tenKhoa?: string;
    khoaHoc?: string;
    ngayNhapHoc?: string;
}

export const useSinhVienInfo = () => {
    const [data, setData] = useState<SinhVienInfoDTO | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchSinhVienInfo = async () => {
            setLoading(true);
            try {
                // Get from API /api/sv/profile
                const response = await fetch(`${API_URL}/sv/profile`, {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`,
                    },
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.isSuccess && result.data) {
                        setData(result.data);
                    }
                }
            } catch (error) {
            } finally {
                setLoading(false);
            }
        };

        fetchSinhVienInfo();
    }, []);

    return { data, loading };
};