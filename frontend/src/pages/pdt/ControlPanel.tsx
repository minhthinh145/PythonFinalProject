// src/pages/pdt/ControlPanel.tsx
import React from "react";
import { useModalContext } from "../../hook/ModalContext";
import { useTogglePhase } from "../../features/pdt/hooks/useTogglePhase";
import { useResetDemoData } from "../../features/pdt/hooks/useResetDemoData";
import "../../styles/reset.css";
import "../../styles/menu.css";

type ControlPanelProps = {
  statuses?: { key: string; label: string }[];
  onSet?: (key: string) => void;
  onReset?: () => void;
};

const DEFAULT_STATUSES = [
  { key: "de_xuat_phe_duyet", label: "Tiền ghi danh (Đề xuất)" },
  { key: "ghi_danh", label: "Ghi danh" },
  { key: "sap_xep_tkb", label: "Sắp xếp thời khóa biểu" },
  { key: "dang_ky_hoc_phan", label: "Đăng ký học phần" },
  { key: "binh_thuong", label: "Bình thường" },
];

export default function ControlPanel({
  statuses = DEFAULT_STATUSES,
  onSet,
  onReset,
}: ControlPanelProps) {
  const { openNotify, openConfirm } = useModalContext();
  const { toggle, loading } = useTogglePhase();
  const { resetData, loading: resetLoading } = useResetDemoData();

  // ✅ Toggle phase - gọi API qua hook
  const handleTogglePhase = async (phaseKey: string) => {
    const phaseMapping: Record<string, string> = {
      de_xuat_phe_duyet: "de_xuat_phe_duyet",
      ghi_danh: "ghi_danh",
      sap_xep_tkb: "sap_xep_tkb",
      dang_ky_hoc_phan: "dang_ky_hoc_phan",
      binh_thuong: "binh_thuong",
    };

    const backendPhase = phaseMapping[phaseKey] || phaseKey;

    const result = await toggle(backendPhase);

    if (result.isSuccess) {
      const status = result.data?.isEnabled ? "BẬT" : "TẮT";
      const statusColor = result.data?.isEnabled ? "success" : "warning";

      openNotify({
        message: `✅ Đã ${status} phase: ${result.data?.phase}`,
        type: statusColor,
      });

      onSet?.(phaseKey);
    } else {
      openNotify({
        message: `❌ ${result.message || "Không thể toggle phase"}`,
        type: "error",
      });
    }
  };

  // ✅ Reset demo data dùng openConfirm + openNotify
  const handleResetClick = async () => {
    const ok = await (openConfirm
      ? openConfirm({
          message:
            "Hành động này sẽ xóa toàn bộ dữ liệu DEMO (đăng ký, học phí, thời khóa biểu, đề xuất, phases...).\nDữ liệu master (users, môn học, khoa, phòng) vẫn được giữ lại.",
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

    const result = await resetData();

    if (result.isSuccess && result.data) {
      openNotify({
        message: `✅ Reset thành công ${result.data.totalCleared} bảng dữ liệu!`,
        type: "success",
      });

      onReset?.();
      window.location.reload();
    } else {
      openNotify({
        message: `❌ ${result.message || "Không thể reset data"}`,
        type: "error",
      });
    }
  };

  return (
    <section className="main__body">
      <div className="body__title">
        <p className="body__title-text">CONTROL PANEL (DEMO)</p>
      </div>

      <div className="body__inner">
        {/* Header */}
        <div className="cp-row cp-row--head">
          <div className="cp-cell">Tên trạng thái</div>
          <div className="cp-cell cp-cell--right">Thao tác</div>
        </div>

        {/* Rows */}
        {statuses.map((st) => (
          <div className="cp-row" key={st.key}>
            <div className="cp-cell">
              <label className="pos__unset cp-label">
                <span className="cp-dot" aria-hidden />
                {st.label}
              </label>
            </div>
            <div className="cp-cell cp-cell--right">
              <button
                type="button"
                className="btn__chung h__40__w__100"
                onClick={() => handleTogglePhase(st.key)}
                disabled={loading}
              >
                {loading ? "..." : "Toggle"}
              </button>
            </div>
          </div>
        ))}

        {/* Footer - Reset Button dùng ConfirmRoot */}
        <div className="cp-footer" style={{ marginTop: 16 }}>
          <button
            type="button"
            className="btn-cancel h__40__w__100"
            onClick={handleResetClick}
            disabled={resetLoading}
          >
            {resetLoading ? "Đang reset..." : "Reset Data"}
          </button>
        </div>

        <p style={{ marginTop: 16, color: "#6b7280", fontSize: 14 }}>
          <strong>⚠️ Lưu ý:</strong> API này toggle phase của{" "}
          <strong>học kỳ hiện hành</strong>. Chỉ dùng cho mục đích demo/testing.
        </p>
      </div>
    </section>
  );
}
