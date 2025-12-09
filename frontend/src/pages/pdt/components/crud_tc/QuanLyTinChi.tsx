import React, { useEffect, useMemo, useState } from "react";
import "../../../../styles/reset.css";
import "../../../../styles/menu.css";
import { useModalContext } from "../../../../hook/ModalContext";
import {
  useChinhSachTinChi,
  useDanhSachKhoa,
  useDanhSachNganh,
  useTinhHocPhiHangLoat,
} from "../../../../features/pdt/hooks";
import type { HocKyItemDTO } from "../../../../features/common/types";
import {
  useHocKyNienKhoa,
  useHocKyHienHanh,
} from "../../../../features/common/hooks";
const formatCurrency = (v: number) =>
  (isFinite(v) ? v : 0).toLocaleString("vi-VN", {
    style: "currency",
    currency: "VND",
  });

export default function QuanLyTinChi() {
  const { openNotify, openConfirm } = useModalContext();

  // ========= Custom Hooks =========
  const {
    data: chinhSachs,
    loading: loadingCS,
    createChinhSach,
    updateChinhSach,
  } = useChinhSachTinChi();
  const { data: khoas, loading: loadingKhoa } = useDanhSachKhoa();
  const { data: hocKyNienKhoas, loading: loadingHocKy } = useHocKyNienKhoa();
  const { data: hocKyHienHanh, loading: loadingHocKyHienHanh } =
    useHocKyHienHanh();
  const { tinhHocPhi, loading: calculatingFee } = useTinhHocPhiHangLoat(); // ✅ Add

  // ========= State =========
  const [selectedNienKhoa, setSelectedNienKhoa] = useState<string>("");
  const [selectedKhoaId, setSelectedKhoaId] = useState("");
  const [form, setForm] = useState({
    hocKyId: "",
    khoaId: "",
    nganhId: "",
    phiMoiTinChi: "",
  });

  // ✅ State for editing
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingValue, setEditingValue] = useState<string>("");

  // ========= Computed - Flatten học kỳ =========
  const nienKhoas = useMemo(
    () => Array.from(new Set(hocKyNienKhoas.map((nk) => nk.tenNienKhoa))),
    [hocKyNienKhoas]
  );

  const flatHocKys = useMemo(() => {
    const result: (HocKyItemDTO & { tenNienKhoa: string })[] = [];

    hocKyNienKhoas.forEach((nienKhoa) => {
      nienKhoa.hocKy.forEach((hk) => {
        result.push({
          ...hk,
          tenNienKhoa: nienKhoa.tenNienKhoa,
        });
      });
    });

    return result;
  }, [hocKyNienKhoas]);

  const hocKysBySelectedNK = useMemo(
    () => flatHocKys.filter((hk) => hk.tenNienKhoa === selectedNienKhoa),
    [flatHocKys, selectedNienKhoa]
  );

  // ========= ✅ Fetch Ngành theo Khoa VÀ HocKyId =========
  const { data: nganhs } = useDanhSachNganh(form.hocKyId, selectedKhoaId);

  // ========= Auto-select học kỳ hiện hành =========
  useEffect(() => {
    // ✅ Đợi cả 2 APIs load xong
    if (loadingHocKy || loadingHocKyHienHanh) return;

    // ✅ Chỉ auto-select 1 lần (khi form.hocKyId còn trống)
    if (form.hocKyId) return;

    // ✅ Cần cả 2 data
    if (!hocKyHienHanh || flatHocKys.length === 0) return;

    // ✅ Tìm học kỳ trong flatHocKys
    const foundHocKy = flatHocKys.find((hk) => hk.id === hocKyHienHanh.id);

    if (foundHocKy) {
      setSelectedNienKhoa(foundHocKy.tenNienKhoa);
      setForm((f) => ({ ...f, hocKyId: foundHocKy.id }));
    } else {
      // Không tìm thấy học kỳ
    }
  }, [
    hocKyHienHanh,
    flatHocKys,
    loadingHocKy,
    loadingHocKyHienHanh,
    form.hocKyId,
  ]);

  // ========= Reset ngành khi đổi khoa hoặc học kỳ =========
  useEffect(() => {
    setForm((f) => ({ ...f, nganhId: "" }));
  }, [selectedKhoaId, form.hocKyId]);

  // ========= Submit Form =========
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.hocKyId) {
      openNotify({
        message: "Vui lòng chọn 'Niên khóa' và 'Học kỳ áp dụng'",
        type: "warning",
      });
      return;
    }

    if (!form.phiMoiTinChi) {
      openNotify({
        message: "Vui lòng nhập 'Phí mỗi tín chỉ'",
        type: "warning",
      });
      return;
    }

    const confirmed = await openConfirm({
      message: "Bạn chắc chắn muốn lưu chính sách này?",
      confirmText: "Lưu",
      cancelText: "Hủy",
    });

    if (!confirmed) return;

    const success = await createChinhSach({
      hocKyId: form.hocKyId,
      khoaId: form.khoaId || null,
      nganhId: form.nganhId || null,
      phiMoiTinChi: Number(form.phiMoiTinChi),
    });

    if (success) {
      setForm({
        hocKyId: "",
        khoaId: "",
        nganhId: "",
        phiMoiTinChi: "",
      });
      setSelectedNienKhoa("");
      setSelectedKhoaId("");
    }
  };

  // ✅ Handle edit
  const handleStartEdit = (id: string, currentValue: number) => {
    setEditingId(id);
    setEditingValue(currentValue.toString());
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingValue("");
  };

  const handleSaveEdit = async (id: string) => {
    const phiMoiTinChi = Number(editingValue);

    if (isNaN(phiMoiTinChi) || phiMoiTinChi < 0) {
      openNotify({ message: "Vui lòng nhập số tiền hợp lệ", type: "warning" });
      return;
    }

    const confirmed = await openConfirm({
      message: `Bạn chắc chắn muốn cập nhật phí thành ${formatCurrency(
        phiMoiTinChi
      )}?`,
      confirmText: "Cập nhật",
      cancelText: "Hủy",
    });

    if (!confirmed) return;

    const success = await updateChinhSach(id, phiMoiTinChi);

    if (success) {
      setEditingId(null);
      setEditingValue("");
    }
  };

  // ✅ Handle tính học phí hàng loạt
  const handleTinhHocPhi = async () => {
    if (!form.hocKyId) {
      openNotify({
        message: "Vui lòng chọn học kỳ trước khi tính học phí",
        type: "warning",
      });
      return;
    }

    const confirmed = await openConfirm({
      message: `Bạn chắc chắn muốn tính học phí hàng loạt cho học kỳ này?\n\nHệ thống sẽ tính toán học phí cho tất cả sinh viên đã đăng ký trong học kỳ.`,
      confirmText: "Tính học phí",
      cancelText: "Hủy",
    });

    if (!confirmed) return;

    await tinhHocPhi(form.hocKyId);
  };

  const loading =
    loadingCS || loadingKhoa || loadingHocKy || loadingHocKyHienHanh;

  return (
    <div style={{ padding: 16 }}>
      {/* ✅ Show loading state */}
      {loading && (
        <p style={{ textAlign: "center", padding: 20 }}>Đang tải dữ liệu...</p>
      )}

      {!loading && (
        <>
          {/* FORM */}
          <form
            onSubmit={handleSubmit}
            className="df"
            style={{
              gap: 8,
              alignItems: "center",
              flexWrap: "wrap",
              marginBottom: 16,
            }}
          >
            <div className="df ">
              {/* Niên khóa */}
              <select
                className="form__select mr_8"
                value={selectedNienKhoa}
                onChange={(e) => {
                  setSelectedNienKhoa(e.target.value);
                  setForm((f) => ({ ...f, hocKyId: "" }));
                }}
              >
                <option value="">-- Chọn niên khóa --</option>
                {nienKhoas.map((nk) => (
                  <option key={nk} value={nk}>
                    {nk}
                  </option>
                ))}
              </select>

              {/* Học kỳ */}
              <select
                className="form__select"
                value={form.hocKyId}
                onChange={(e) =>
                  setForm((f) => ({ ...f, hocKyId: e.target.value }))
                }
                disabled={!selectedNienKhoa}
              >
                <option value="">-- Học kỳ áp dụng --</option>
                {hocKysBySelectedNK.map((hk) => (
                  <option key={hk.id} value={hk.id}>
                    {hk.tenHocKy}
                  </option>
                ))}
              </select>
            </div>

            <div className="df ">
              {/* Khoa */}
              <select
                className="form__select mr_8"
                value={form.khoaId}
                onChange={(e) => {
                  const val = e.target.value;
                  setSelectedKhoaId(val);
                  setForm((f) => ({ ...f, khoaId: val, nganhId: "" }));
                }}
                disabled={!form.hocKyId} // ✅ Disable if no hocKyId
              >
                <option value="">Áp dụng cho khoa</option>
                {khoas.map((k) => (
                  <option key={k.id} value={k.id}>
                    {k.tenKhoa}
                  </option>
                ))}
              </select>

              {/* Ngành */}
              <select
                className="form__select mr_8"
                value={form.nganhId}
                onChange={(e) =>
                  setForm((f) => ({ ...f, nganhId: e.target.value }))
                }
                disabled={!form.khoaId || !form.hocKyId} // ✅ Disable if no hocKyId or khoaId
              >
                <option value="">Áp dụng cho ngành</option>
                {nganhs.map((n) => (
                  <option key={n.id} value={n.id}>
                    {n.tenNganh}
                  </option>
                ))}
              </select>

              {/* Đơn giá */}
              <input
                className="form__select mr_8"
                type="number"
                min={0}
                step={1000}
                placeholder="Phí mỗi tín chỉ (VND)"
                value={form.phiMoiTinChi}
                onChange={(e) =>
                  setForm((f) => ({ ...f, phiMoiTinChi: e.target.value }))
                }
              />

              <button type="submit" className="btn__chung" disabled={loading}>
                {loading ? "Đang lưu..." : "Lưu chính sách"}
              </button>
            </div>
          </form>

          {/* ✅ HEADER - Nút tính học phí (Option B) */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
              paddingBottom: 12,
              borderBottom: "2px solid #e5e7eb",
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: "16px",
                fontWeight: 600,
                color: "#172b4d",
              }}
            >
              Danh sách chính sách tín chỉ
            </h3>

            <button
              type="button"
              onClick={handleTinhHocPhi}
              disabled={calculatingFee || !form.hocKyId}
              className="btn__update h__40"
              style={{
                padding: "8px 16px",
                fontSize: "14px",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
                <path
                  fill="currentColor"
                  d="M392 176L248 176L210.7 101.5C208.9 97.9 208 93.9 208 89.9C208 75.6 219.6 64 233.9 64L406.1 64C420.4 64 432 75.6 432 89.9C432 93.9 431.1 97.9 429.3 101.5L392 176zM233.6 224L406.4 224L455.1 264.6C521.6 320 560 402 560 488.5C560 536.8 520.8 576 472.5 576L167.4 576C119.2 576 80 536.8 80 488.5C80 402 118.4 320 184.9 264.6L233.6 224zM324 288C313 288 304 297 304 308L304 312C275.2 312.3 252 335.7 252 364.5C252 390.2 270.5 412.1 295.9 416.3L337.6 423.3C343.6 424.3 348 429.5 348 435.6C348 442.5 342.4 448.1 335.5 448.1L280 448C269 448 260 457 260 468C260 479 269 488 280 488L304 488L304 492C304 503 313 512 324 512C335 512 344 503 344 492L344 487.3C369 483.2 388 461.6 388 435.5C388 409.8 369.5 387.9 344.1 383.7L302.4 376.7C296.4 375.7 292 370.5 292 364.4C292 357.5 297.6 351.9 304.5 351.9L352 351.9C363 351.9 372 342.9 372 331.9C372 320.9 363 311.9 352 311.9L344 311.9L344 307.9C344 296.9 335 287.9 324 287.9z"
                />
              </svg>
              {calculatingFee ? "Đang tính..." : "Tính học phí hàng loạt"}
            </button>
          </div>

          {/* BẢNG DANH SÁCH */}
          <table className="table" style={{ color: "#172b4d" }}>
            <thead>
              <tr>
                <th>STT</th>
                <th>Học kỳ</th>
                <th>Khoa</th>
                <th>Ngành</th>
                <th>Phí / tín chỉ</th>
                <th>Hiệu lực</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {chinhSachs.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: 20 }}>
                    Chưa có chính sách
                  </td>
                </tr>
              ) : (
                chinhSachs.map((d, i) => (
                  <tr key={d.id}>
                    <td>{i + 1}</td>
                    <td>{d.hocKy?.tenHocKy || "-"}</td>
                    <td>{d.khoa?.tenKhoa || "-"}</td>
                    <td>{d.nganhHoc?.tenNganh || "-"}</td>

                    {/* ✅ Editable cell */}
                    <td>
                      {editingId === d.id ? (
                        <input
                          type="number"
                          min={0}
                          step={1000}
                          value={editingValue}
                          onChange={(e) => setEditingValue(e.target.value)}
                          style={{
                            width: "120px",
                            padding: "4px 8px",
                            border: "1px solid #0c4874",
                            borderRadius: "4px",
                          }}
                          autoFocus
                        />
                      ) : (
                        formatCurrency(d.phiMoiTinChi)
                      )}
                    </td>

                    <td>
                      {d.ngayHieuLuc
                        ? new Date(d.ngayHieuLuc).toLocaleDateString("vi-VN")
                        : "-"}
                      {" → "}
                      {d.ngayHetHieuLuc
                        ? new Date(d.ngayHetHieuLuc).toLocaleDateString("vi-VN")
                        : "-"}
                    </td>

                    {/* ✅ Action buttons */}
                    <td>
                      {editingId === d.id ? (
                        <div
                          style={{
                            display: "flex",
                            gap: "8px",
                            justifyContent: "center",
                          }}
                        >
                          <button
                            className="btn__chung df_center gap_10"
                            onClick={() => handleSaveEdit(d.id)}
                            style={{ padding: "4px 12px", fontSize: "13px" }}
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 448 512"
                            >
                              <path
                                fill="#ffffff"
                                d="M64 32C28.7 32 0 60.7 0 96L0 416c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-242.7c0-17-6.7-33.3-18.7-45.3L352 50.7C340 38.7 323.7 32 306.7 32L64 32zm32 96c0-17.7 14.3-32 32-32l160 0c17.7 0 32 14.3 32 32l0 64c0 17.7-14.3 32-32 32l-160 0c-17.7 0-32-14.3-32-32l0-64zM224 288a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"
                              />
                            </svg>{" "}
                            Lưu
                          </button>
                          <button
                            className="btn-cancel"
                            onClick={handleCancelEdit}
                            style={{ padding: "4px 12px", fontSize: "13px" }}
                          >
                            Hủy
                          </button>
                        </div>
                      ) : (
                        <button
                          className="btn__update df_center gap_10 h__40"
                          onClick={() => handleStartEdit(d.id, d.phiMoiTinChi)}
                          style={{ padding: "4px 12px", fontSize: "13px" }}
                        >
                          <svg
                            className="df_center"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 640 640"
                          >
                            <path
                              fill="currentColor"
                              d="M416.9 85.2L372 130.1L509.9 268L554.8 223.1C568.4 209.6 576 191.2 576 172C576 152.8 568.4 134.4 554.8 120.9L519.1 85.2C505.6 71.6 487.2 64 468 64C448.8 64 430.4 71.6 416.9 85.2zM338.1 164L122.9 379.1C112.2 389.8 104.4 403.2 100.3 417.8L64.9 545.6C62.6 553.9 64.9 562.9 71.1 569C77.3 575.1 86.2 577.5 94.5 575.2L222.3 539.7C236.9 535.6 250.2 527.9 261 517.1L476 301.9L338.1 164z"
                            ></path>
                          </svg>{" "}
                          Chỉnh sửa
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
