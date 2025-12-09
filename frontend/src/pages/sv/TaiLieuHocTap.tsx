import { useState } from "react";
import { useSVTaiLieu } from "../../features/sv/hooks/useSVTaiLieu";
import SVTaiLieuList from "./components/SVTaiLieuList";
import HocKySelector from "../../components/HocKySelector";
import type { LopDaDangKyWithTaiLieuDTO } from "../../features/sv/types";

export default function TaiLieuHocTap() {
  const [selectedHocKyId, setSelectedHocKyId] = useState<string>("");

  const { lopDaDangKy, selectedLop, taiLieu, loading, error, selectLop } =
    useSVTaiLieu(selectedHocKyId || null);

  const handleHocKyChange = (hocKyId: string) => {
    setSelectedHocKyId(hocKyId);
  };

  return (
    <section className="main__body">
      <div className="body__title">
        <p className="body__title-text">TÀI LIỆU HỌC TẬP</p>
      </div>
      <div className="body__inner" style={{ padding: "24px" }}>
        {/* Học kỳ selector */}
        <div
          className="selecy__duyethp__container"
          style={{ marginBottom: "24px" }}
        >
          <HocKySelector onHocKyChange={handleHocKyChange} />
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              padding: "16px",
              backgroundColor: "#fef2f2",
              border: "1px solid #fecaca",
              borderRadius: "8px",
              color: "#dc2626",
              marginBottom: "16px",
            }}
          >
            ❌ {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <p style={{ color: "#6b7280" }}>⏳ Đang tải dữ liệu...</p>
          </div>
        )}

        {/* Main content - 2 columns layout */}
        {!loading && selectedHocKyId && (
          <div
            style={{ display: "flex", gap: "24px", alignItems: "flex-start" }}
          >
            {/* Left column - Danh sách lớp */}
            <div
              style={{
                flex: "0 0 350px",
                backgroundColor: "white",
                borderRadius: "8px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                padding: "16px",
                maxHeight: "calc(100vh - 200px)",
                overflowY: "auto",
              }}
            >
              <h2
                style={{
                  fontSize: "16px",
                  fontWeight: 600,
                  marginBottom: "16px",
                  color: "#124874",
                }}
              >
                Lớp học phần đã đăng ký
              </h2>

              {lopDaDangKy.length === 0 && (
                <p style={{ color: "#9ca3af", fontSize: "14px" }}>
                  Chưa có lớp nào được đăng ký
                </p>
              )}

              {lopDaDangKy.map((lop: LopDaDangKyWithTaiLieuDTO) => (
                <div
                  key={lop.lopHocPhanId}
                  onClick={() => selectLop(lop)}
                  style={{
                    padding: "12px",
                    marginBottom: "8px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    backgroundColor:
                      selectedLop?.lopHocPhanId === lop.lopHocPhanId
                        ? "#dbeafe"
                        : "#f9fafb",
                    border:
                      selectedLop?.lopHocPhanId === lop.lopHocPhanId
                        ? "2px solid #3b82f6"
                        : "1px solid #e5e7eb",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    if (selectedLop?.lopHocPhanId !== lop.lopHocPhanId) {
                      e.currentTarget.style.backgroundColor = "#f3f4f6";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedLop?.lopHocPhanId !== lop.lopHocPhanId) {
                      e.currentTarget.style.backgroundColor = "#f9fafb";
                    }
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: "4px",
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: "14px",
                          fontWeight: 600,
                          color: "#0c4874",
                          marginBottom: "4px",
                        }}
                      >
                        {lop.tenMon}
                      </div>

                      <div style={{ fontSize: "12px", color: "#CF373D" }}>
                        {lop.maMon} - {lop.maLop}
                      </div>

                      {/* SVG + tên giảng viên */}
                      <div
                        style={{
                          fontSize: "12px",
                          color: "#0c4874",
                          marginTop: "4px",
                          display: "flex", // 👈 hàng ngang
                          alignItems: "center", // 👈 căn giữa theo chiều dọc
                          gap: 4, // khoảng cách icon - text (tuỳ chọn)
                        }}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 640 512"
                          style={{
                            width: 14, // 👈 chỉnh size icon
                            height: 14,
                            flexShrink: 0, // không bị ép nhỏ
                          }}
                        >
                          <path
                            fill="#0c4874"
                            d="M128 96c0-35.3 28.7-64 64-64l352 0c35.3 0 64 28.7 64 64l0 240-96 0 0-16c0-17.7-14.3-32-32-32l-64 0c-17.7 0-32 14.3-32 32l0 16-129.1 0c10.9-18.8 17.1-40.7 17.1-64 0-70.7-57.3-128-128-128-5.4 0-10.8 .3-16 1l0-49zM333 448c-5.1-24.2-16.3-46.1-32.1-64L608 384c0 35.3-28.7 64-64 64l-211 0zM64 272a80 80 0 1 1 160 0 80 80 0 1 1 -160 0zM0 480c0-53 43-96 96-96l96 0c53 0 96 43 96 96 0 17.7-14.3 32-32 32L32 512c-17.7 0-32-14.3-32-32z"
                          />
                        </svg>

                        <span>{lop.giangVien}</span>
                      </div>
                    </div>

                    {/* Badge số tài liệu */}
                    {lop.taiLieu.length > 0 && (
                      <div
                        style={{
                          backgroundColor: "#3b82f6",
                          color: "white",
                          borderRadius: "12px",
                          padding: "2px 8px",
                          fontSize: "12px",
                          fontWeight: 600,
                          minWidth: "24px",
                          textAlign: "center",
                        }}
                      >
                        {lop.taiLieu.length}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Right column - Danh sách tài liệu */}
            <div
              style={{
                flex: 1,
                backgroundColor: "white",
                borderRadius: "8px",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                padding: "16px",
                minHeight: "400px",
              }}
            >
              {selectedLop ? (
                <>
                  <div
                    style={{
                      marginBottom: "16px",
                      paddingBottom: "12px",
                      borderBottom: "1px solid #e5e7eb",
                    }}
                  >
                    <h2
                      style={{
                        fontSize: "18px",
                        fontWeight: 600,
                        color: "#0c4874",
                        marginBottom: "4px",
                      }}
                    >
                      {selectedLop.tenMon}
                    </h2>
                    <p style={{ fontSize: "14px", color: "#CF373D" }}>
                      {selectedLop.maMon} - {selectedLop.maLop} ({" "}
                      {selectedLop.soTinChi} TC)
                    </p>
                  </div>

                  <SVTaiLieuList
                    documents={taiLieu}
                    lhpId={selectedLop.lopHocPhanId}
                  />
                </>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "400px",
                    color: "#9ca3af",
                  }}
                >
                  <svg
                    width="64"
                    height="64"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    style={{ marginBottom: "16px" }}
                  >
                    <path
                      d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z"
                      fill="#d1d5db"
                    />
                  </svg>
                  <p>Chọn một lớp để xem tài liệu</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* No học kỳ selected */}
        {!loading && !selectedHocKyId && (
          <div
            style={{
              textAlign: "center",
              padding: "60px 20px",
              backgroundColor: "white",
              borderRadius: "8px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
            }}
          >
            <p style={{ color: "#6b7280" }}>
              Vui lòng chọn học kỳ để xem tài liệu
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
