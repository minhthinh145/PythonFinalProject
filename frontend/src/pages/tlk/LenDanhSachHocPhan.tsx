// apps/frontend/src/pages/tlk/LenDanhSachHocPhan.tsx
import React, { useEffect, useMemo, useState } from "react";
import Fuse from "fuse.js";
import { useModalContext } from "../../hook/ModalContext";
import { tlkAPI } from "../../features/tlk/api/tlkAPI";
import type {
  MonHocDTO,
  GiangVienDTO,
  HocKyHienHanhResponse,
} from "../../features/tlk/types";

type DeXuatRow = { monHocId: string; soLuongLop: number; giangVienId: string };

const LenDanhSachHocPhan: React.FC = () => {
  const { openNotify } = useModalContext();

  const [monHocs, setMonHocs] = useState<MonHocDTO[]>([]);
  const [filteredMonHocs, setFilteredMonHocs] = useState<MonHocDTO[]>([]);
  const [searchValue, setSearchValue] = useState("");
  const [selectedRows, setSelectedRows] = useState<DeXuatRow[]>([]);
  const [giangVienByMon, setGiangVienByMon] = useState<
    Record<string, GiangVienDTO[]>
  >({});
  const [hocKyHienHanh, setHocKyHienHanh] =
    useState<HocKyHienHanhResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  /* ================= Fuse search ================= */
  const fuse = useMemo(
    () =>
      new Fuse<MonHocDTO>(monHocs, {
        keys: ["ma_mon", "ten_mon"],
        threshold: 0.3,
      }),
    [monHocs]
  );

  /* ================= currentSemester: đọc field an toàn ================= */
  const currentSemester = useMemo(() => {
    if (!hocKyHienHanh) return null;

    const hk: any = hocKyHienHanh;

    // Thử nhiều kiểu key: camelCase, snake_case, hoặc flatten
    const tenHocKy: string =
      hk.tenHocKy ?? hk.ten_hoc_ky ?? hk.ten_hoc_ky_hien_hanh ?? "";

    const tenNienKhoa: string =
      hk.nienKhoa?.tenNienKhoa ?? hk.nienKhoa ?? hk.nien_khoa ?? "";

    // Nếu cả 2 đều rỗng thì coi như không có học kỳ hiện hành
    if (!tenHocKy && !tenNienKhoa) return null;

    return {
      tenHocKy,
      tenNienKhoa,
    };
  }, [hocKyHienHanh]);

  const currentSemesterText = currentSemester
    ? ` (Niên khóa ${currentSemester.tenNienKhoa}, Học kỳ ${currentSemester.tenHocKy})`
    : "";

  /* ================= API calls ================= */
  const fetchHocKyHienHanh = async () => {
    try {
      const result = await tlkAPI.getHocKyHienHanh();
      if (result.isSuccess && result.data) {
        setHocKyHienHanh(result.data);
        // Nếu muốn debug, có thể bật log:
        // console.log("hocKyHienHanh >>>", result.data);
        // Không notify info để đỡ spam
      } else {
        openNotify?.("Không lấy được học kỳ hiện hành", "warning");
        setHocKyHienHanh(null);
      }
    } catch (err) {
      console.error(err);
      openNotify?.("Không lấy được học kỳ hiện hành", "warning");
      setHocKyHienHanh(null);
    }
  };

  const fetchMonHocs = async () => {
    try {
      const result = await tlkAPI.getMonHoc();
      if (result.isSuccess && Array.isArray(result.data)) {
        setMonHocs(result.data);
        setFilteredMonHocs(result.data);
        // Không cần notify "Đã tải X môn học"
      } else {
        setMonHocs([]);
        setFilteredMonHocs([]);
        openNotify?.("Không có dữ liệu môn học", "warning");
      }
    } catch (err) {
      console.error(err);
      setMonHocs([]);
      setFilteredMonHocs([]);
      openNotify?.("Lỗi khi tải danh sách môn học", "error");
    }
  };

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        await Promise.all([fetchHocKyHienHanh(), fetchMonHocs()]);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  /* ================= Handlers ================= */
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const q = searchValue.trim();
    if (!q) {
      setFilteredMonHocs(monHocs);
      // Không cần notify “Đã làm mới danh sách môn học”
      return;
    }
    const results = fuse.search(q).map((r) => r.item);
    setFilteredMonHocs(results);
    if (results.length === 0) {
      openNotify?.("Không tìm thấy môn học phù hợp", "warning");
    }
    // Không cần notify “Tìm thấy X môn học”
  };

  const toggleSelectMon = async (monHocId: string) => {
    const existed = selectedRows.find((r) => r.monHocId === monHocId);
    if (existed) {
      setSelectedRows((prev) => prev.filter((r) => r.monHocId !== monHocId));
      // Không cần notify “Đã bỏ chọn môn”
      return;
    }
    // nạp danh sách GV cho môn (nếu chưa có)
    if (!giangVienByMon[monHocId]) {
      try {
        const result = await tlkAPI.getGiangVien(monHocId);
        setGiangVienByMon((prev) => ({
          ...prev,
          [monHocId]: result.data ?? [],
        }));
      } catch (err) {
        console.error(err);
        openNotify?.(
          "Không tải được danh sách giảng viên cho môn này",
          "error"
        );
      }
    }
    setSelectedRows((prev) => [
      ...prev,
      { monHocId, soLuongLop: 1, giangVienId: "" },
    ]);
    // Không cần notify “Đã thêm môn vào danh sách đề xuất”
  };

  const onChangeGV = (monHocId: string, giangVienId: string) =>
    setSelectedRows((prev) =>
      prev.map((r) => (r.monHocId === monHocId ? { ...r, giangVienId } : r))
    );

  const addDeXuat = async (monHoc: MonHocDTO, giangVienId: string) => {
    try {
      setSubmitting(true);

      const result = await tlkAPI.createDeXuatHocPhan({
        maHocPhan: monHoc.id,
        maGiangVien: giangVienId || "",
      });

      if (result.isSuccess) {
        openNotify?.(`Đã thêm đề xuất: ${monHoc.ten_mon}`, "success");
        await fetchMonHocs(); // Reload
      } else {
        openNotify?.(result.message || "Thêm đề xuất thất bại", "error");
      }
    } catch (err: any) {
      console.error(err);
      openNotify?.(err?.message || "Lỗi khi thêm đề xuất", "error");
    } finally {
      setSubmitting(false);
    }
  };

  /* ================= Render ================= */
  return (
    <section className="main__body">
      <div className="body__title">
        <p className="body__title-text">
          LÊN DANH SÁCH HỌC PHẦN {currentSemesterText}
        </p>
      </div>

      <div className="body__inner">
        <form className="search-form" onSubmit={handleSearch}>
          <div className="form__group form__group--ctt">
            <input
              type="text"
              id="search-input"
              className="form__input"
              placeholder=" "
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
            />
            <label
              htmlFor="search-input"
              className="form__floating-label top__21"
            >
              Nhập thông tin môn học
            </label>
          </div>
          <button
            type="submit"
            className="btn__chung w__200 h__40"
            disabled={loading}
          >
            {loading ? "Đang tải..." : "Tìm kiếm"}
          </button>
        </form>

        <table className="table table--ldshp" style={{ color: "#172b4d" }}>
          <thead>
            <tr>
              <th className="c-chon">Chọn</th>
              <th className="c-ma">Mã MH</th>
              <th className="c-ten">Tên MH</th>
              <th className="c-stc">STC</th>
              <th className="c-gv">Giảng viên</th>
              <th className="c-action">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {filteredMonHocs.map((mh) => {
              const checked = selectedRows.some((r) => r.monHocId === mh.id);
              const current = selectedRows.find((r) => r.monHocId === mh.id);
              const gvs = giangVienByMon[mh.id] ?? [];
              return (
                <tr key={mh.id}>
                  <td>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleSelectMon(mh.id)}
                    />
                  </td>
                  <td>{mh.ma_mon}</td>
                  <td>{mh.ten_mon}</td>
                  <td>{mh.so_tin_chi}</td>
                  <td>
                    {checked && (
                      <select
                        className="h__40"
                        value={current?.giangVienId ?? ""}
                        onChange={(e) => onChangeGV(mh.id, e.target.value)}
                      >
                        <option value="">-- Chọn --</option>
                        {gvs.map((gv) => (
                          <option key={gv.id} value={gv.id}>
                            {gv.ho_ten}
                          </option>
                        ))}
                      </select>
                    )}
                  </td>

                  <td>
                    {checked ? (
                      <button
                        className="btn__update h__40"
                        onClick={() =>
                          addDeXuat(mh, current?.giangVienId || "")
                        }
                        disabled={submitting}
                      >
                        {submitting ? "Đang xử lý..." : "Thêm"}
                      </button>
                    ) : (
                      <span style={{ opacity: 0.5 }}></span>
                    )}
                  </td>
                </tr>
              );
            })}
            {filteredMonHocs.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: "center" }}>
                  Không tìm thấy môn học nào phù hợp.
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {selectedRows.length > 0 && (
          <button
            className="btn__chung"
            // onClick={addDeXuat} // TODO: nếu sau này muốn gửi batch
            disabled={submitting}
            style={{ marginTop: "1rem", padding: "8px 16px" }}
          >
            {submitting ? "Đang gửi..." : "Xác nhận đề xuất"}
          </button>
        )}
      </div>
    </section>
  );
};

export default LenDanhSachHocPhan;
