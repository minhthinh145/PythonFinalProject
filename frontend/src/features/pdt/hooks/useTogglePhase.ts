import { useState } from "react";
import { pdtApi } from "../api/pdtApi";
import type { ServiceResult } from "../../common/ServiceResult";

/**
 * Hook toggle phase (Demo)
 */
export const useTogglePhase = () => {
    const [loading, setLoading] = useState(false);

    const toggle = async (phase: string, hocKyId?: string): Promise<ServiceResult<{ isEnabled: boolean; phase: string }>> => {
        setLoading(true);
        try {
            const result = await pdtApi.togglePhase({ hocKyId, phase });
            return result;
        } catch (error: any) {
            return {
                isSuccess: false,
                message: error.message || "Lỗi khi toggle phase",
            };
        } finally {
            setLoading(false);
        }
    };

    return { toggle, loading };
};
