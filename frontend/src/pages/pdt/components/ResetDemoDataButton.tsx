import { useState } from "react";
import { useResetDemoData } from "../../../features/pdt/hooks/useResetDemoData";
import "./ResetDemoDataButton.css";

interface ResetDemoDataButtonProps {
    onResetComplete?: () => void;
}

/**
 * Reset Demo Data Button Component
 * Shows a confirmation dialog before resetting all demo data
 */
export const ResetDemoDataButton = ({ onResetComplete }: ResetDemoDataButtonProps) => {
    const { resetData, loading } = useResetDemoData();
    const [showConfirm, setShowConfirm] = useState(false);
    const [result, setResult] = useState<{
        success: boolean;
        message: string;
        details?: { totalCleared: number; errors: string[] };
    } | null>(null);

    const handleReset = async () => {
        const response = await resetData();
        
        if (response.isSuccess && response.data) {
            setResult({
                success: true,
                message: `Reset thành công ${response.data.totalCleared} bảng`,
                details: {
                    totalCleared: response.data.totalCleared,
                    errors: response.data.errors,
                },
            });
            onResetComplete?.();
        } else {
            setResult({
                success: false,
                message: response.message || "Lỗi khi reset data",
            });
        }
        
        setShowConfirm(false);
    };

    return (
        <div className="reset-demo-data">
            {!showConfirm && !result && (
                <button
                    type="button"
                    className="reset-demo-data__btn reset-demo-data__btn--warning"
                    onClick={() => setShowConfirm(true)}
                    disabled={loading}
                >
                    🔄 Reset Demo Data
                </button>
            )}

            {showConfirm && (
                <div className="reset-demo-data__confirm">
                    <p className="reset-demo-data__confirm-text">
                        ⚠️ <strong>Cảnh báo:</strong> Hành động này sẽ xóa toàn bộ dữ liệu demo
                        (đăng ký, học phí, thời khóa biểu, đề xuất, phases...).
                        <br />
                        <em>Dữ liệu master (users, môn học, khoa, phòng) sẽ được giữ lại.</em>
                    </p>
                    <div className="reset-demo-data__confirm-actions">
                        <button
                            type="button"
                            className="reset-demo-data__btn reset-demo-data__btn--danger"
                            onClick={handleReset}
                            disabled={loading}
                        >
                            {loading ? "Đang reset..." : "✅ Xác nhận Reset"}
                        </button>
                        <button
                            type="button"
                            className="reset-demo-data__btn reset-demo-data__btn--secondary"
                            onClick={() => setShowConfirm(false)}
                            disabled={loading}
                        >
                            ❌ Hủy
                        </button>
                    </div>
                </div>
            )}

            {result && (
                <div className={`reset-demo-data__result reset-demo-data__result--${result.success ? 'success' : 'error'}`}>
                    <p>{result.message}</p>
                    {result.details?.errors && result.details.errors.length > 0 && (
                        <ul className="reset-demo-data__errors">
                            {result.details.errors.map((err, idx) => (
                                <li key={idx}>{err}</li>
                            ))}
                        </ul>
                    )}
                    <button
                        type="button"
                        className="reset-demo-data__btn reset-demo-data__btn--secondary"
                        onClick={() => setResult(null)}
                    >
                        OK
                    </button>
                </div>
            )}
        </div>
    );
};
