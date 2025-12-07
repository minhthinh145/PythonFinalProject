import React, { useMemo, useRef, useState } from "react";
import "../../styles/reset.css";
import "../../styles/menu.css";
import { useModalContext } from "../../hook/ModalContext";
import HocKySelector from "../../components/HocKySelector";
import { useDanhSachKhoa } from "../../features/pdt/hooks";
import { useDmNganh } from "../../features/pdt/hooks/useDmNganh";
import {
  useBaoCaoOverview,
  useBaoCaoDangKyTheoKhoa,
  useBaoCaoDangKyTheoNganh,
  useBaoCaoTaiGiangVien,
  useBaoCaoExport,
} from "../../features/pdt/hooks/useBaoCaoThongKe";
import {
  DangKyTheoKhoaChart,
  DangKyTheoNganhChart,
  TaiGiangVienChart,
  TaiChinhChart,
} from "./components/charts";

/* ========= Utils ========= */
const currency = (v: number) =>
  (isFinite(v) ? v : 0).toLocaleString("vi-VN", {
    style: "currency",
    currency: "VND",
  });

/** Lấy PNG DataURL từ phần tử SVG của Recharts để gửi vào PDF */
async function getChartPNGFromContainer(
  container: HTMLElement,
  width = 1200,
  height = 600
): Promise<string> {
  const svg = container.querySelector("svg");
  if (!svg) throw new Error("Không tìm thấy SVG trong biểu đồ");

  const serializer = new XMLSerializer();
  const svgStr = serializer.serializeToString(svg);
  const svgBlob = new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(svgBlob);

  const img = new Image();
  img.crossOrigin = "anonymous";
  const dataUrl: string = await new Promise((resolve, reject) => {
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return reject(new Error("Không thể khởi tạo canvas"));
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      const out = canvas.toDataURL("image/png");
      URL.revokeObjectURL(url);
      resolve(out);
    };
    img.onerror = (e) => reject(e);
    img.src = url;
  });
  return dataUrl;
}

/* ====== Small UI pieces ====== */
function StatCard({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div
      style={{
        minWidth: 220,
        padding: "10px 14px",
        borderRadius: 12,
        background: "#fff",
        boxShadow: "0 1px 6px rgba(0,0,0,0.06)",
      }}
    >
      <div style={{ fontSize: 12, color: "#666" }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>{value}</div>
    </div>
  );
}

function ChartCard({
  title,
  chartRef,
  height = 320,
  children,
  conclusion,
}: {
  title: string;
  chartRef: React.RefObject<HTMLDivElement>;
  height?: number;
  children: React.ReactNode;
  conclusion?: string;
}) {
  return (
    <section
      className="chart-card"
      style={{
        background: "#fff",
        borderRadius: 12,
        boxShadow: "0 1px 6px rgba(0,0,0,0.06)",
        padding: 12,
      }}
    >
      <h3 style={{ margin: "0 0 8px", color: "#294e8dff", fontWeight: 600 }}>
        {title}
      </h3>
      <div ref={chartRef} style={{ width: "100%", height }}>
        {children}
      </div>
      {conclusion && (
        <p style={{ marginTop: 6 }}>
          <b>Kết luận:</b> {conclusion}
        </p>
      )}
    </section>
  );
}

/* ========= Component ========= */
export default function BaoCaoThongKe() {
  const { openNotify } = useModalContext();

  // ✅ Custom hooks
  const { data: khoas, loading: loadingKhoa } = useDanhSachKhoa();
  const { data: nganhs, loading: loadingNganh } = useDmNganh(); // ✅ Use new hook

  const {
    data: overview,
    loading: loadingOverview,
    fetch: fetchOverview,
  } = useBaoCaoOverview();
  const {
    data: dkTheoKhoa,
    ketLuan: ketLuanKhoa,
    fetch: fetchDKKhoa,
  } = useBaoCaoDangKyTheoKhoa();
  const {
    data: dkTheoNganh,
    ketLuan: ketLuanNganh,
    fetch: fetchDKNganh,
  } = useBaoCaoDangKyTheoNganh();
  const {
    data: taiGV,
    ketLuan: ketLuanGV,
    fetch: fetchTaiGV,
  } = useBaoCaoTaiGiangVien();
  const { loading: exporting, exportExcel, exportPDF } = useBaoCaoExport();

  const [hocKyId, setHocKyId] = useState<string>("");
  const [khoaId, setKhoaId] = useState<string>("");
  const [nganhId, setNganhId] = useState<string>("");

  const filteredNganhs = useMemo(
    () => (khoaId ? nganhs.filter((n) => n.khoaId === khoaId) : nganhs),
    [nganhs, khoaId]
  );

  // chart refs (wrap container divs to convert to PNG later)
  const refKhoa = useRef<HTMLDivElement | null>(null);
  const refNganh = useRef<HTMLDivElement | null>(null);
  const refGV = useRef<HTMLDivElement | null>(null);
  const refFinance = useRef<HTMLDivElement | null>(null);

  const loadReports = async () => {
    if (!hocKyId) {
      openNotify({
        message: "Vui lòng chọn học kỳ để thống kê.",
        type: "warning",
      });
      return;
    }

    // ✅ FIX: Chỉ truyền các params có giá trị
    const overviewParams: {
      hoc_ky_id: string;
      khoa_id?: string;
      nganh_id?: string;
    } = {
      hoc_ky_id: hocKyId,
    };
    if (khoaId) overviewParams.khoa_id = khoaId;
    if (nganhId) overviewParams.nganh_id = nganhId; // ✅ Chỉ thêm nếu có giá trị

    await Promise.all([
      fetchOverview(overviewParams),
      fetchDKKhoa(hocKyId),
      fetchDKNganh({ hocKyId, khoaId: khoaId || undefined }), // ✅ undefined thay vì empty string
      fetchTaiGV({ hocKyId, khoaId: khoaId || undefined }),
    ]);
  };

  const handleExportExcel = async () => {
    if (!hocKyId) {
      openNotify({ message: "Chưa chọn học kỳ.", type: "warning" });
      return;
    }

    // ✅ FIX: Chỉ truyền các params có giá trị
    const params: { hoc_ky_id: string; khoa_id?: string; nganh_id?: string } = {
      hoc_ky_id: hocKyId,
    };
    if (khoaId) params.khoa_id = khoaId;
    if (nganhId) params.nganh_id = nganhId;

    const success = await exportExcel(params);

    if (!success) {
      openNotify({ message: "Xuất Excel thất bại", type: "error" });
    }
  };

  const handleExportPDF = async () => {
    if (!hocKyId) {
      openNotify({ message: "Chưa chọn học kỳ.", type: "warning" });
      return;
    }

    try {
      const charts: { name: string; dataUrl: string }[] = [];

      if (refKhoa.current) {
        charts.push({
          name: "Đăng ký theo khoa",
          dataUrl: await getChartPNGFromContainer(refKhoa.current),
        });
      }
      if (refNganh.current) {
        charts.push({
          name: "Đăng ký theo ngành",
          dataUrl: await getChartPNGFromContainer(refNganh.current),
        });
      }
      if (refGV.current) {
        charts.push({
          name: "Tải giảng viên (Top)",
          dataUrl: await getChartPNGFromContainer(refGV.current),
        });
      }
      if (refFinance.current) {
        charts.push({
          name: "Tài chính học phí",
          dataUrl: await getChartPNGFromContainer(refFinance.current),
        });
      }

      // ✅ FIX: Chỉ truyền khoa_id và nganh_id nếu có giá trị
      const pdfData: {
        hoc_ky_id: string;
        khoa_id?: string;
        nganh_id?: string;
        charts: { name: string; dataUrl: string }[];
      } = {
        hoc_ky_id: hocKyId,
        charts,
      };
      if (khoaId) pdfData.khoa_id = khoaId;
      if (nganhId) pdfData.nganh_id = nganhId;

      const success = await exportPDF(pdfData);

      if (!success) {
        openNotify({ message: "Xuất PDF thất bại", type: "error" });
      }
    } catch (e: any) {
      openNotify({ message: `Lỗi: ${e.message}`, type: "error" });
    }
  };

  // finance chart data
  const financeData = useMemo(() => {
    if (!overview) return [];
    return [
      {
        name: "Học phí",
        "Thực thu": overview.taiChinh.thuc_thu,
        "Kỳ vọng": overview.taiChinh.ky_vong,
      },
    ];
  }, [overview]);

  // UI
  const loading = loadingOverview || loadingKhoa;

  return (
    <div style={{ padding: 16 }}>
      {/* Filters */}
      <div
        className="df"
        style={{
          gap: 8,
          alignItems: "center",
          flexWrap: "wrap",
          marginBottom: 12,
        }}
      >
        {/* ✅ Use HocKySelector without auto-select */}
        <HocKySelector onHocKyChange={setHocKyId} autoSelectCurrent={false} />

        <div>
          {/* Khoa */}
          <select
            className="form__input form__select mr_8"
            value={khoaId}
            onChange={(e) => {
              setKhoaId(e.target.value);
              setNganhId("");
            }}
          >
            <option value="">Tất cả khoa</option>
            {khoas.map((k) => (
              <option key={k.id} value={k.id}>
                {k.tenKhoa}
              </option>
            ))}
          </select>

          {/* Ngành */}
          <select
            className="form__input form__select"
            value={nganhId}
            onChange={(e) => setNganhId(e.target.value)}
            disabled={!khoaId}
          >
            <option value="">Tất cả ngành</option>
            {filteredNganhs.map((n) => (
              <option key={n.id} value={n.id}>
                {n.tenNganh}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={loadReports}
          className="btn__update h__40"
          disabled={loading}
        >
          {loading ? "Đang tải..." : "Tải thống kê"}
        </button>

        <button
          onClick={handleExportExcel}
          className="btn__update h__40"
          disabled={exporting}
        >
          {exporting ? "Đang xuất..." : "Xuất Excel"}
        </button>

        <button
          onClick={handleExportPDF}
          className="btn__update h__40"
          disabled={exporting}
        >
          {exporting ? "Đang xuất..." : "Xuất PDF"}
        </button>
      </div>

      {/* Overview cards */}
      {overview && (
        <div
          className="df"
          style={{
            gap: 12,
            flexWrap: "wrap",
            marginBottom: 12,
          }}
        >
          <StatCard label="SV đã đăng ký (unique)" value={overview.svUnique} />
          <StatCard label="Bản ghi đăng ký" value={overview.soDangKy} />
          <StatCard label="Lớp học phần mở" value={overview.soLopHocPhan} />
          <StatCard
            label="Thực thu"
            value={currency(overview.taiChinh.thuc_thu)}
          />
          <StatCard
            label="Kỳ vọng"
            value={currency(overview.taiChinh.ky_vong)}
          />
        </div>
      )}

      {/* Charts Grid: 2 cột -> 2 hàng cho 4 chart */}
      {loading ? (
        <p>Đang tải dữ liệu...</p>
      ) : (
        <div
          className="charts-grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            gap: 12,
          }}
        >
          {/* Hàng 1 */}
          <ChartCard
            title="Đăng ký theo khoa"
            chartRef={refKhoa as React.RefObject<HTMLDivElement>}
            height={320}
            conclusion={ketLuanKhoa || undefined}
          >
            <DangKyTheoKhoaChart data={dkTheoKhoa} />
          </ChartCard>

          <ChartCard
            title={`Đăng ký theo ngành ${
              khoaId ? "(lọc theo khoa đã chọn)" : ""
            }`}
            chartRef={refNganh as React.RefObject<HTMLDivElement>}
            height={320}
            conclusion={ketLuanNganh || undefined}
          >
            <DangKyTheoNganhChart data={dkTheoNganh} />
          </ChartCard>

          {/* Hàng 2 */}
          <ChartCard
            title={`Tải giảng viên ${khoaId ? "(lọc theo khoa đã chọn)" : ""}`}
            chartRef={refGV as React.RefObject<HTMLDivElement>}
            height={360}
            conclusion={ketLuanGV || undefined}
          >
            <TaiGiangVienChart data={taiGV} />
          </ChartCard>

          <ChartCard
            title="Tài chính học phí"
            chartRef={refFinance as React.RefObject<HTMLDivElement>}
            height={320}
            conclusion={overview?.ketLuan || undefined}
          >
            <TaiChinhChart data={financeData} formatCurrency={currency} />
          </ChartCard>
        </div>
      )}
    </div>
  );
}
