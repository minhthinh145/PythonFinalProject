import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../../styles/reset.css";
import "../../styles/menu.css";
import { useGVLopHocPhanDetail } from "../../features/gv/hooks";
import TaiLieuUpload from "./components/TaiLieuUpload";
import TaiLieuList from "./components/TaiLieuList";

export default function GVLopHocPhanDetail() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<"docs" | "sv" | "grades">("docs");

  const {
    info,
    students,
    documents,
    grades,
    loading,
    submitting,
    uploadProgress,
    setGrades,
    uploadMultipleFiles,
    deleteDocument,
    saveGrades,
    getDocumentUrl,
  } = useGVLopHocPhanDetail(id!);

  return (
    <section className="main__body">
      <div className="body__title">
        <p className="body__title-text">
          {info
            ? `QUẢN LÝ LỚP ${info.ma_lop} — ${info.hoc_phan.mon_hoc.ma_mon} ${info.hoc_phan.mon_hoc.ten_mon}`
            : "QUẢN LÝ LỚP HỌC PHẦN"}
        </p>
      </div>

      <div className="body__inner">
        {/* Nút trở về */}

        {loading && (
          <p style={{ textAlign: "center", padding: 20 }}>
            Đang tải dữ liệu...
          </p>
        )}

        {!loading && info && (
          <>
            {/* Tabs */}
            <div className="tabs" style={{ marginBottom: 12 }}>
              <button
                className="btn__chung h__40 w__60 mr_20 tab-btn"
                onClick={() => navigate(-1)} // quay lại trang trước
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512">
                  <path
                    fill="#ffffffff"
                    d="M9.4 278.6c-12.5-12.5-12.5-32.8 0-45.3l128-128c9.2-9.2 22.9-11.9 34.9-6.9S192 115.1 192 128l0 64 336 0c26.5 0 48 21.5 48 48l0 32c0 26.5-21.5 48-48 48l-336 0 0 64c0 12.9-7.8 24.6-19.8 29.6s-25.7 2.2-34.9-6.9l-128-128z"
                  />
                </svg>
              </button>

              <button
                className={`btn__update h__40 w__100 mr_20 tab-btn ${
                  tab === "docs" ? "active" : ""
                }`}
                onClick={() => setTab("docs")}
              >
                Tài liệu
              </button>

              <button
                className={`btn__update h__40 w__100 mr_20 tab-btn ${
                  tab === "sv" ? "active" : ""
                }`}
                onClick={() => setTab("sv")}
              >
                Sinh viên
              </button>

              <button
                className={`btn__update h__40 w__100 mr_20 tab-btn ${
                  tab === "grades" ? "active" : ""
                }`}
                onClick={() => setTab("grades")}
              >
                Điểm
              </button>
            </div>

            {/* Tài liệu */}
            {tab === "docs" && (
              <div>
                <TaiLieuUpload
                  onUpload={uploadMultipleFiles}
                  uploading={submitting}
                  uploadProgress={uploadProgress}
                />

                <TaiLieuList
                  documents={documents}
                  onDelete={deleteDocument}
                  onGetUrl={getDocumentUrl}
                  submitting={submitting}
                  lhpId={id!}
                />
              </div>
            )}

            {/* Sinh viên */}
            {tab === "sv" && (
              <div className="table__wrapper">
                <table className="table" style={{ color: "#172b4d" }}>
                  <thead>
                    <tr>
                      <th>MSSV</th>
                      <th>Họ tên</th>
                      <th>Lớp</th>
                      <th>Email</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((s) => (
                      <tr key={s.mssv}>
                        <td>{s.mssv}</td>
                        <td>{s.hoTen}</td>
                        <td>{s.lop || ""}</td>
                        <td>{s.email}</td>
                      </tr>
                    ))}
                    {students.length === 0 && (
                      <tr>
                        <td
                          colSpan={4}
                          style={{ textAlign: "center", padding: 20 }}
                        >
                          Chưa có sinh viên đăng ký.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Điểm */}
            {tab === "grades" && (
              <div>
                <div className="table__wrapper">
                  <table className="table" style={{ color: "#172b4d" }}>
                    <thead>
                      <tr>
                        <th>MSSV</th>
                        <th>Họ tên</th>
                        <th>Điểm</th>
                      </tr>
                    </thead>
                    <tbody>
                      {students.map((s) => (
                        <tr key={s.id}>
                          {/* Use UUID as key */}
                          <td>{s.mssv}</td>
                          <td>{s.hoTen}</td>
                          <td style={{ maxWidth: 120 }}>
                            <input
                              type="number"
                              min={0}
                              max={10}
                              step={0.1}
                              value={grades[s.id] ?? ""}
                              onChange={(e) =>
                                setGrades((g) => ({
                                  ...g,
                                  // Use UUID as key
                                  [s.id]:
                                    e.target.value === ""
                                      ? ""
                                      : Number(e.target.value),
                                }))
                              }
                            />
                          </td>
                        </tr>
                      ))}
                      {students.length === 0 && (
                        <tr>
                          <td
                            colSpan={3}
                            style={{ textAlign: "center", padding: 20 }}
                          >
                            Không có sinh viên để nhập điểm.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                <div style={{ marginTop: 12 }}>
                  <button
                    className="btn__update h__40 w__100"
                    onClick={saveGrades}
                    disabled={submitting}
                  >
                    {submitting ? "Đang lưu..." : "Lưu điểm"}
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}
