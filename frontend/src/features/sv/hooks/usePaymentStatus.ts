import { useState, useEffect } from "react";
import { svApi } from "../api/svApi";
import type { PaymentStatusResponse } from "../types";

/**
 * ✅ Hook poll payment status (every 1s)
 * ✅ Stop polling when status is final (success, failed, cancelled)
 */
export const usePaymentStatus = (
    orderId: string,
    maxAttempts = 20, // ✅ Tăng từ 15 → 20
    interval = 1000,
    initialDelay = 2000 // ✅ THÊM: Đợi 2s trước khi poll lần đầu
) => {
    const [status, setStatus] = useState<PaymentStatusResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!orderId) {
            setLoading(false);
            setError("Không có mã đơn hàng");
            return;
        }

        let attempts = 0;
        let intervalId: ReturnType<typeof setInterval>;
        let initialTimeoutId: ReturnType<typeof setTimeout>;

        const checkStatus = async () => {
            attempts++;


            try {
                const result = await svApi.getPaymentStatus(orderId);

                if (result.isSuccess && result.data) {
                    const currentStatus = result.data.status;


                    setStatus(result.data);

                    // ✅ Stop polling if final status
                    if (
                        currentStatus === "success" ||
                        currentStatus === "failed" ||
                        currentStatus === "cancelled"
                    ) {
                        clearInterval(intervalId);
                        setLoading(false);
                        return true; // ✅ Signal success
                    }
                } else {
                    console.warn(`⚠️ API error: ${result.message}`);
                }

                return false; // Continue polling
            } catch (err: any) {
                console.error("❌ Error checking payment:", err);
                // ✅ Don't stop on first error - retry
                return false;
            }
        };

        const startPolling = () => {
            // ✅ First check immediately (after initial delay)
            checkStatus().then((shouldStop) => {
                if (shouldStop) return;

                // ✅ Start interval polling
                intervalId = setInterval(async () => {
                    const shouldStop = await checkStatus();

                    if (shouldStop || attempts >= maxAttempts) {
                        clearInterval(intervalId);
                        setLoading(false);

                        if (attempts >= maxAttempts && status?.status === "pending") {
                            setError("Không thể xác nhận kết quả. Vui lòng kiểm tra lại sau.");
                        }
                    }
                }, interval);
            });
        };

        // ✅ Add initial delay before first poll
        initialTimeoutId = setTimeout(startPolling, initialDelay);

        // ✅ Cleanup
        return () => {
            clearTimeout(initialTimeoutId);
            if (intervalId) clearInterval(intervalId);
        };
    }, [orderId, maxAttempts, interval, initialDelay]);

    return { status, loading, error };
};
