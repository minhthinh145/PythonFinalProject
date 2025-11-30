import React, { useEffect, useMemo, useState } from "react";
import { useModalContext } from "../../../../hook/ModalContext";
import ModalThemSinhVien from "./ModalThemSinhVien";
import ModalCapNhatSinhVien from "./ModalCapNhatSinhVien";
import "../../../../styles/reset.css";
import "../../../../styles/menu.css";
import { pdtApi } from "../../../../features/pdt/api/pdtApi";
import { commonApi } from "../../../../features/common/api/commonApi";

type SinhVien = {
  id: string;
  maSoSinhVien: string;
  hoTen: string;
  lop: string;
  khoaHoc: string;
  tenKhoa: string;
  tenNganh: string;
  trangThaiHoatDong: boolean;
};

type Khoa = { id: string; tenKhoa: string };
type Nganh = { id: string; tenNganh: string; khoaId: string };

const QuanLySinhVien: React.FC = () => {
  const { openNotify, openConfirm } = useModalContext();

  const [allSinhVien, setAllSinhVien] = useState<SinhVien[]>([]);
  const [search, setSearch] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const [khoaList, setKhoaList] = useState<Khoa[]>([]);
  const [nganhList, setNganhList] = useState<Nganh[]>([]);

  const [filterKhoa, setFilterKhoa] = useState<string>("");
  const [filterNganh, setFilterNganh] = useState<string>("");
  const [filterLop, setFilterLop] = useState<string>("");

  const [showAddModal, setShowAddModal] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);

  // LOAD DATA
  const loadSinhVien = async () => {
    try {
      const res = await pdtApi.getSinhVien();
      if (!res.isSuccess) throw new Error(res.message);
      const items: SinhVien[] = res.data?.items ?? [];
      setAllSinhVien(items);
    } catch (e: any) {
      console.error(e);
      openNotify?.("Không thể tải danh sách sinh viên", "error");
    }
  };

  const loadDanhMuc = async () => {
    try {
      const [khoaRes, nganhRes] = await Promise.all([
        pdtApi.getDanhSachKhoa(),
        commonApi.getDanhSachNganh(),
      ]);

      if (!khoaRes.isSuccess) throw new Error(khoaRes.message);
      if (!nganhRes.isSuccess) throw new Error(nganhRes.message);

      setKhoaList(khoaRes.data || []);
      
      // Map NganhDTO (snake_case) to Nganh (camelCase)
      const mappedNganh = (nganhRes.data || []).map((n: any) => ({
        id: n.id,
        tenNganh: n.ten_nganh || n.tenNganh,
        khoaId: n.khoa_id || n.khoaId,
      }));
      setNganhList(mappedNganh);
    } catch (error) {
      console.error("Error loading data:", error);
      openNotify?.("Không thể tải danh sách Khoa/Ngành", "error");
    }
  };

  useEffect(() => {
    loadSinhVien();
    loadDanhMuc();
  }, []);

  // FILTER CLIENT-SIDE
  const filteredData = useMemo(() => {
    let list = allSinhVien;

    if (filterKhoa) {
      const selectedKhoa = khoaList.find((k) => k.id === filterKhoa);
      if (selectedKhoa) {
        list = list.filter((sv) => sv.tenKhoa === selectedKhoa.tenKhoa);
      }
    }

    if (filterNganh) {
      const selectedNganh = nganhList.find((n) => n.id === filterNganh);
      if (selectedNganh) {
        list = list.filter((sv) => sv.tenNganh === selectedNganh.tenNganh);
      }
    }

    if (filterLop.trim()) {
      list = list.filter((sv) =>
        sv.lop?.toLowerCase().includes(filterLop.toLowerCase())
      );
    }

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((sv) =>
        [sv.hoTen, sv.maSoSinhVien, sv.tenKhoa, sv.tenNganh, sv.lop]
          .filter(Boolean)
          .some((v) => v!.toLowerCase().includes(q))
      );
    }

    return list;
  }, [
    allSinhVien,
    filterKhoa,
    filterNganh,
    filterLop,
    search,
    khoaList,
    nganhList,
  ]);

  // DELETE
  const handleDeleteSinhVien = async (id: string) => {
    const ok = await (openConfirm
      ? openConfirm({
          message: "Bạn có chắc muốn xoá sinh viên này?",
          variant: "danger",
          confirmText: "Xoá",
          cancelText: "Hủy",
        })
      : Promise.resolve(confirm("Xoá sinh viên này?")));
    if (!ok) return;

    try {
      const res = await pdtApi.deleteSinhVien(id);
      if (res.isSuccess) {
        openNotify?.("Đã xoá sinh viên", "success");
        setAllSinhVien((prev) => prev.filter((s) => s.id !== id));
      } else {
        throw new Error(res.message);
      }
    } catch {
      openNotify?.("Lỗi khi xoá sinh viên", "error");
    }
  };

  // JSX
  return (
    <section className="">
      <div className="">
        <fieldset className="fieldset__quanly">
          <legend>Tổng: {filteredData.length} sinh viên</legend>

          {/* + Thêm */}
          <button className="btn__add" onClick={() => setShowAddModal(true)}>
            +
          </button>

          {/* - Lọc */}
          <button
            className="btn__sort"
            onClick={() => setShowFilters((s) => !s)}
          >
            -
          </button>

          {/* Bộ lọc */}
          {showFilters && (
            <div className="filter-group selecy__duyethp__container mt_20">
              <select
                className="form__input form__select mr_20"
                value={filterKhoa}
                onChange={(e) => {
                  setFilterKhoa(e.target.value);
                  setFilterNganh("");
                }}
              >
                <option value="">-- Tất cả khoa --</option>
                {khoaList.map((k) => (
                  <option key={k.id} value={k.id}>
                    {k.tenKhoa}
                  </option>
                ))}
              </select>

              <select
                className="form__input form__select mr_20"
                value={filterNganh}
                onChange={(e) => setFilterNganh(e.target.value)}
                disabled={!filterKhoa}
              >
                <option value="">-- Tất cả ngành --</option>
                {nganhList
                  .filter((n) => !filterKhoa || n.khoaId === filterKhoa)
                  .map((n) => (
                    <option key={n.id} value={n.id}>
                      {n.tenNganh}
                    </option>
                  ))}
              </select>

              <input
                className="form__input form__select mr_20"
                placeholder="Lọc theo lớp..."
                value={filterLop}
                onChange={(e) => setFilterLop(e.target.value)}
              />

              <button
                className="btn__chung h__40 w__100"
                onClick={() => {
                  setFilterKhoa("");
                  setFilterNganh("");
                  setFilterLop("");
                }}
              >
                Xoá lọc
              </button>
            </div>
          )}

          {/* Tìm kiếm */}
          <div className="form__group form__group__quanly mtb_20 ">
            <input
              type="text"
              className="form__input h__40 w__100p"
              placeholder="Tìm kiếm theo tên, MSSV, khoa, ngành, lớp..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Bảng */}
          <table className="table table_quanly">
            <thead>
              <tr>
                <th>Họ và Tên</th>
                <th>MSSV</th>
                <th>Lớp</th>
                <th>Khoa</th>
                <th>Ngành</th>
                <th>Khóa học</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((sv) => (
                <tr key={sv.id}>
                  <td>{sv.hoTen}</td>
                  <td>{sv.maSoSinhVien}</td>
                  <td>{sv.lop}</td>
                  <td>{sv.tenKhoa}</td>
                  <td>{sv.tenNganh}</td>
                  <td>{sv.khoaHoc}</td>
                  <td className="w40">
                    <div className="btn__quanly__container">
                      <button
                        className="btn-cancel w50__h20"
                        onClick={() => handleDeleteSinhVien(sv.id)}
                      >
                        Xóa
                      </button>
                      <button
                        className="btn__update w20__h20"
                        onClick={() => setEditId(sv.id)}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 640 640"
                        >
                          <path
                            fill="currentColor"
                            d="M416.9 85.2L372 130.1L509.9 268L554.8 223.1C568.4 209.6 576 191.2 576 172C576 152.8 568.4 134.4 554.8 120.9L519.1 85.2C505.6 71.6 487.2 64 468 64C448.8 64 430.4 71.6 416.9 85.2zM338.1 164L122.9 379.1C112.2 389.8 104.4 403.2 100.3 417.8L64.9 545.6C62.6 553.9 64.9 562.9 71.1 569C77.3 575.1 86.2 577.5 94.5 575.2L222.3 539.7C236.9 535.6 250.2 527.9 261 517.1L476 301.9L338.1 164z"
                          />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredData.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center" }}>
                    Không có sinh viên nào
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </fieldset>
      </div>

      {/* Modals */}
      {showAddModal && (
        <ModalThemSinhVien
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
          onCreated={() => {
            setShowAddModal(false);
            loadSinhVien();
          }}
        />
      )}

      {editId && (
        <ModalCapNhatSinhVien
          id={editId}
          isOpen={!!editId}
          onClose={() => {
            setEditId(null);
            loadSinhVien();
          }}
        />
      )}
    </section>
  );
};

export default QuanLySinhVien;
