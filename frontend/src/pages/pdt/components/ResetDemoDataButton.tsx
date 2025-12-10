// src/pages/pdt/ResetDemoDataButton.tsx
import { useState } from "react";
import { useResetDemoData } from "../../../features/pdt/hooks/useResetDemoData";
import { useModalContext } from "../../../hook/ModalContext"; // ⚠️ chỉnh path nếu cần
import "./ResetDemoDataButton.css";

interface ResetDemoDataButtonProps {
  onResetComplete?: () => void;
}

/**
 * Reset Demo Data Button Component
 * Dùng ModalContext: openConfirm + openNotify
 */
export const ResetDemoDataButton = ({
  onResetComplete,
}: ResetDemoDataButtonProps) => {
  const { resetData, loading } = useResetDemoData();
  const { openNotify, openConfirm } = useModalContext();
  // (giữ state result nếu muốn hiển thị chi tiết lỗi dưới nút)
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    details?: { totalCleared: number; errors: string[] };
  } | null>(null);

  const handleClick = async () => {
    // Hỏi xác nhận bằng ConfirmRoot (fallback window.confirm nếu chưa mount)
    const ok = await (openConfirm
      ? openConfirm({
          title: "Reset dữ liệu demo?",
          message:
            "⚠️ Hành động này sẽ xóa toàn bộ dữ liệu DEMO (đăng ký, học phí, TKB, đề xuất, phases...).\nDữ liệu master (users, môn học, khoa, phòng) vẫn được giữ lại.",
          confirmText: "Reset ngay",
          cancelText: "Hủy",
          variant: "danger",
        })
      : Promise.resolve(
          window.confirm(
            "Bạn có chắc muốn RESET toàn bộ dữ liệu demo (trừ dữ liệu master)?"
          )
        ));

    if (!ok) return;

    const response = await resetData();

    if (response.isSuccess && response.data) {
      const { totalCleared, errors } = response.data;

      // Toast thành công
      openNotify?.(
        `Đã reset demo data cho ${totalCleared} bảng${
          errors?.length ? " (có một số lỗi nhỏ)" : ""
        }`,
        "success"
      );

      setResult({
        success: true,
        message: `Reset thành công ${totalCleared} bảng.`,
        details: { totalCleared, errors },
      });

      onResetComplete?.();
    } else {
      const msg = response.message || "Lỗi khi reset demo data";

      // Toast lỗi
      openNotify?.(msg, "error");

      setResult({
        success: false,
        message: msg,
      });
    }
  };

  return (
    <div className="reset-demo-data">
      <button
        type="button"
        className="reset-demo-data__btn reset-demo-data__btn--warning"
        onClick={handleClick}
        disabled={loading}
      >
        {loading ? "Đang reset..." : "🔄 Reset Demo Data"}
      </button>

      {/* Phần hiển thị thêm chi tiết nếu muốn giữ lại */}
      {result && (
        <div
          className={`reset-demo-data__result reset-demo-data__result--${
            result.success ? "success" : "error"
          }`}
        >
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
