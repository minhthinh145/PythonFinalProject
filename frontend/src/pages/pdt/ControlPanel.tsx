// src/pages/pdt/ControlPanel.tsx
import React, { useState } from "react";
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
  const { openNotify } = useModalContext();
  const { toggle, loading } = useTogglePhase();
  const { resetData, loading: resetLoading } = useResetDemoData();
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  // ✅ Toggle phase - gọi API qua hook
  const handleTogglePhase = async (phaseKey: string) => {
    // Map frontend keys to backend enums (legacy values)
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

      // ✅ Call parent callback if provided
      onSet?.(phaseKey);
    } else {
      openNotify({
        message: `❌ ${result.message || "Không thể toggle phase"}`,
        type: "error",
      });
    }
  };

  // ✅ Reset demo data - gọi API thực sự
  const handleReset = async () => {
    const result = await resetData();
    
    if (result.isSuccess && result.data) {
      openNotify({
        message: `✅ Reset thành công ${result.data.totalCleared} bảng dữ liệu!`,
        type: "success",
      });
      
      // Call parent callback and reload
      onReset?.();
      window.location.reload();
    } else {
      openNotify({
        message: `❌ ${result.message || "Không thể reset data"}`,
        type: "error",
      });
    }
    
    setShowResetConfirm(false);
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
        {statuses.map((st, idx) => (
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

        {/* Footer - Reset Button */}
        <div className="cp-footer" style={{ marginTop: 16 }}>
          {!showResetConfirm ? (
            <button
              type="button"
              className="btn-cancel h__40__w__100"
              onClick={() => setShowResetConfirm(true)}
              disabled={resetLoading}
              style={{ background: "#f59e0b", color: "white" }}
            >
              🔄 Reset Demo Data
            </button>
          ) : (
            <div style={{ 
              padding: 16, 
              background: "#fff3cd", 
              borderRadius: 8,
              border: "1px solid #ffc107"
            }}>
              <p style={{ marginBottom: 12, color: "#92400e" }}>
                ⚠️ <strong>Cảnh báo:</strong> Xóa toàn bộ dữ liệu demo?
                <br />
                <em style={{ fontSize: 13 }}>
                  (Giữ: users, môn học, khoa, phòng. Xóa: đăng ký, học phí, TKB...)
                </em>
              </p>
              <div style={{ display: "flex", gap: 10 }}>
                <button
                  type="button"
                  onClick={handleReset}
                  disabled={resetLoading}
                  style={{ 
                    padding: "8px 16px", 
                    background: "#dc2626", 
                    color: "white",
                    border: "none",
                    borderRadius: 6,
                    cursor: "pointer"
                  }}
                >
                  {resetLoading ? "Đang reset..." : "✅ Xác nhận Reset"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowResetConfirm(false)}
                  disabled={resetLoading}
                  style={{ 
                    padding: "8px 16px", 
                    background: "#6b7280", 
                    color: "white",
                    border: "none",
                    borderRadius: 6,
                    cursor: "pointer"
                  }}
                >
                  ❌ Hủy
                </button>
              </div>
            </div>
          )}
        </div>

        {/* ✅ Note */}
        <p style={{ marginTop: 16, color: "#6b7280", fontSize: 14 }}>
          <strong>⚠️ Lưu ý:</strong> API này toggle phase của{" "}
          <strong>học kỳ hiện hành</strong>. Chỉ dùng cho mục đích demo/testing.
        </p>
      </div>
    </section>
  );
}

