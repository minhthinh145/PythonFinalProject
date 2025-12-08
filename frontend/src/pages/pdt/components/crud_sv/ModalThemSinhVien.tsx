import React, { useEffect, useState } from "react";
import { useModalContext } from "../../../../hook/ModalContext";
import { useDanhSachNganh } from "../../../../features/common/hooks"; // ✅ Import hook
import "../../../../styles/reset.css";
import "../../../../styles/menu.css";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onCreated?: () => void;
};

type Khoa = { id: string; tenKhoa: string };

const API = import.meta.env.VITE_API_URL || "/api";
const withToken = (init: RequestInit = {}) => {
  const headers = new Headers(init.headers || {});
  const token = localStorage.getItem("token");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  headers.set("Content-Type", "application/json");
  return { ...init, headers };
};

export const ModalThemSinhVien: React.FC<Props> = ({
  isOpen,
  onClose,
  onCreated,
}) => {
  const { openNotify } = useModalContext();

  const [danhSachKhoa, setDanhSachKhoa] = useState<Khoa[]>([]);
  const [formData, setFormData] = useState({
    maSoSinhVien: "",
    hoTen: "",
    tenDangNhap: "",
    matKhau: "",
    lop: "",
    khoaId: "",
    nganhId: "",
    khoaHoc: "",
    ngayNhapHoc: "",
  });

  // ✅ Use hook - fetch ngành when khoaId changes
  const { data: danhSachNganh, loading: loadingNganh } = useDanhSachNganh(
    formData.khoaId || undefined
  );

  // ✅ Debug log
  useEffect(() => {
  }, [danhSachNganh, loadingNganh]);

  const [excelFile, setExcelFile] = useState<File | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    (async () => {
      try {
        const khoaRes = await fetch(`${API}/pdt/khoa`, withToken());
        const kjson = await khoaRes.json();

        const khoaData =
          kjson?.data?.items || kjson?.data || kjson?.items || kjson || [];

        setDanhSachKhoa(Array.isArray(khoaData) ? khoaData : []);
      } catch (error) {
        console.error("❌ [Modal] Error loading khoa:", error);
        openNotify?.("Không thể tải danh sách Khoa", "error");
      }
    })();
  }, [isOpen, openNotify]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    if (name === "khoaId") {
      setFormData((s) => ({ ...s, [name]: value, nganhId: "" }));
    } else {
      setFormData((s) => ({ ...s, [name]: value }));
    }
  };

  const handleSubmit = async () => {
    const tenDangNhap = formData.tenDangNhap || formData.maSoSinhVien || "";
    const matKhau = formData.matKhau || formData.maSoSinhVien || "";

    if (
      !formData.maSoSinhVien ||
      !formData.hoTen ||
      !tenDangNhap ||
      !matKhau ||
      !formData.khoaId
    ) {
      openNotify?.("Vui lòng nhập đủ MSSV, Họ tên, Khoa", "warning");
      return;
    }

    const payload = {
      tenDangNhap,
      matKhau,
      hoTen: formData.hoTen,
      maSoSinhVien: formData.maSoSinhVien,
      maKhoa: formData.khoaId,
      lop: formData.lop || undefined,
      khoaHoc: formData.khoaHoc || undefined,
      ngayNhapHoc: formData.ngayNhapHoc || undefined,
      maNganh: formData.nganhId || undefined,
      trangThaiHoatDong: true,
    };

    try {
      const res = await fetch(
        `${API}/pdt/sinh-vien`,
        withToken({ method: "POST", body: JSON.stringify(payload) })
      );
      const json = await res.json();
      if (json.success || json.isSuccess) {
        openNotify?.("Thêm sinh viên thành công", "success");
        onCreated?.();
      } else {
        openNotify?.(json.message || "Thêm sinh viên thất bại", "error");
      }
    } catch {
      openNotify?.("Không thể gọi API", "error");
    }
  };

  // ============= IMPORT EXCEL (API: POST /api/import/sinh-vien) =============
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setExcelFile(f);
  };

  const handleUploadExcel = async () => {
    if (!excelFile) {
      openNotify?.("Vui lòng chọn file Excel (  .xls, .xlsx)", "info");
      return;
    }
    try {
      const form = new FormData();
      form.append("file", excelFile);

      const res = await fetch(`${API}/pdt/sinh-vien/import/excel`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
        },
        body: form,
      });

      const json = await res.json();
      if (!json.isSuccess) {
        openNotify?.(json.message || "Import thất bại", "error");
        return;
      }

      const summary = json.data?.summary;
      const results = json.data?.results || [];
      const created = summary?.created ?? 0;
      const failed = summary?.failed ?? 0;

      const firstErrors = results
        .filter((r: any) => r.status === "failed")
        .slice(0, 5)
        .map((r: any) => `Dòng ${r.row}: ${r.error}`)
        .join("\n");

      openNotify?.(
        `Import hoàn tất.\nTạo mới: ${created}\nLỗi: ${failed}${
          failed ? `\n${firstErrors}${results.length > 5 ? "\n..." : ""}` : ""
        }`,
        failed ? "warning" : "success"
      );

      setExcelFile(null);
      // FIX TS2779: không dùng optional chaining ở vế trái
      const el = document.getElementById(
        "excelUpload"
      ) as HTMLInputElement | null;
      if (el) el.value = "";

      onCreated?.();
    } catch {
      openNotify?.("Không thể gọi API import", "error");
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div
        className="modal-overlay"
        onClick={(e) => {
          if (e.target === e.currentTarget) onClose();
        }}
      >
        <div className="modal-popup">
          {" "}
          {/* ✅ Changed back from modal-content */}
          <form onSubmit={(e) => e.preventDefault()}>
            <div className="modal-header">
              <h1>Thêm sinh viên</h1>
              <button type="button" className="md-btn-cancel" onClick={onClose}>
                X
              </button>
            </div>

            {/* MSSV & Tên */}
            <div className="modal-popup-row">
              <div className="form__group ">
                <label className="pos__unset">Mã số sinh viên</label>
                <input
                  name="maSoSinhVien"
                  type="text"
                  value={formData.maSoSinhVien}
                  onChange={handleChange}
                />
              </div>
              <div className="form__group">
                <label className="pos__unset">Tên sinh viên</label>
                <input
                  name="hoTen"
                  type="text"
                  value={formData.hoTen}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Tài khoản */}
            <div className="modal-popup-row">
              <div className="form__group">
                <label className="pos__unset">
                  Tên đăng nhập <small>(mặc định = MSSV nếu bỏ trống)</small>
                </label>
                <input
                  name="tenDangNhap"
                  type="text"
                  value={formData.tenDangNhap}
                  onChange={handleChange}
                />
              </div>
              <div className="form__group">
                <label className="pos__unset">
                  Mật khẩu <small>(mặc định = MSSV nếu bỏ trống)</small>
                </label>
                <input
                  name="matKhau"
                  type="password"
                  value={formData.matKhau}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Lớp - Khoa */}
            <div className="modal-popup-row">
              <div className="form__group">
                <label className="pos__unset">Lớp</label>
                <input
                  name="lop"
                  type="text"
                  value={formData.lop}
                  onChange={handleChange}
                />
              </div>
              <div className="form__group">
                <label className="pos__unset">Khoa</label>
                <select
                  id="md-Khoa"
                  name="khoaId"
                  value={formData.khoaId}
                  onChange={handleChange}
                >
                  <option value="">-- Chọn khoa --</option>
                  {danhSachKhoa.map((khoa) => (
                    <option key={khoa.id} value={khoa.id}>
                      {khoa.tenKhoa}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Ngành - Khóa học */}
            <div className="modal-popup-row">
              <div className="form__group">
                <label className="pos__unset">Ngành</label>
                <select
                  id="md-Nganh"
                  name="nganhId"
                  value={formData.nganhId}
                  onChange={handleChange}
                  disabled={!formData.khoaId || loadingNganh}
                >
                  <option value="">
                    {loadingNganh
                      ? "Đang tải..."
                      : !formData.khoaId
                      ? "Chọn khoa trước"
                      : "-- Chọn ngành --"}
                  </option>
                  {danhSachNganh.map((nganh: any) => (
                    <option key={nganh.id} value={nganh.id}>
                      {nganh.tenNganh || nganh.ten_nganh}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form__group">
                <label className="pos__unset">Khóa học</label>
                <input
                  name="khoaHoc"
                  type="text"
                  value={formData.khoaHoc}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Ngày nhập học & Excel */}
            <div className="modal-popup-row">
              <div className="form__group">
                <label className="pos__unset">Ngày nhập học</label>
                <input
                  name="ngayNhapHoc"
                  type="date"
                  value={formData.ngayNhapHoc}
                  onChange={handleChange}
                />
              </div>
              <div className="form__group">
                <label className="pos__unset">Tải lên file Excel:</label>
                <input
                  id="excelUpload"
                  type="file"
                  accept=".xls,.xlsx"
                  onChange={handleFileChange}
                />
              </div>
            </div>

            {/* Nút */}
            <div className="modal-popup-row">
              <button
                type="button"
                className="md-btn-add"
                onClick={handleSubmit}
              >
                Thêm thủ công
              </button>
              <button
                type="button"
                className="md-btn-add"
                onClick={handleUploadExcel}
              >
                Tải từ Excel
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
};

export default ModalThemSinhVien;
