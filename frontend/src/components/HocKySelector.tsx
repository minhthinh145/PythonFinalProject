import { useEffect, useMemo, useState, useRef } from "react";
import { useHocKyHienHanh, useHocKyNienKhoa } from "../features/common/hooks";
import type { HocKyItemDTO } from "../features/common/types";

interface HocKySelectorProps {
  onHocKyChange: (hocKyId: string) => void;
  disabled?: boolean;
  autoSelectCurrent?: boolean;
}

export default function HocKySelector({
  onHocKyChange,
  disabled = false,
  autoSelectCurrent = true,
}: HocKySelectorProps) {
  const { data: hocKyHienHanh, loading: loadingHienHanh } = useHocKyHienHanh();
  const { data: hocKyNienKhoas, loading: loadingHocKy } = useHocKyNienKhoa();

  const [selectedNienKhoa, setSelectedNienKhoa] = useState<string>("");
  const [selectedHocKyId, setSelectedHocKyId] = useState<string>("");

  const hasAutoSelected = useRef(false);

  const flatHocKys = useMemo(() => {
    const result: (HocKyItemDTO & { tenNienKhoa: string })[] = [];
    hocKyNienKhoas.forEach((nienKhoa) => {
      nienKhoa.hocKy.forEach((hk) => {
        result.push({ ...hk, tenNienKhoa: nienKhoa.tenNienKhoa });
      });
    });
    return result;
  }, [hocKyNienKhoas]);

  useEffect(() => {
    if (hasAutoSelected.current) return;

    if (
      loadingHienHanh ||
      loadingHocKy ||
      !hocKyHienHanh ||
      flatHocKys.length === 0
    ) {
      return;
    }

    if (!autoSelectCurrent) {
      hasAutoSelected.current = true; 
      return;
    }

    const hkHienHanh = flatHocKys.find((hk) => hk.id === hocKyHienHanh.id);

    if (hkHienHanh) {
      setSelectedNienKhoa(hkHienHanh.tenNienKhoa);
      setSelectedHocKyId(hkHienHanh.id);
      onHocKyChange(hkHienHanh.id);
      hasAutoSelected.current = true;
    }
  }, [
    hocKyHienHanh,
    flatHocKys,
    loadingHienHanh,
    loadingHocKy,
    autoSelectCurrent,
  ]);

  useEffect(() => {
    setSelectedHocKyId("");
  }, [selectedNienKhoa]);

  const filteredHocKys = useMemo(
    () =>
      selectedNienKhoa
        ? flatHocKys.filter((hk) => hk.tenNienKhoa === selectedNienKhoa)
        : [],
    [flatHocKys, selectedNienKhoa]
  );

  const handleHocKyChange = (hocKyId: string) => {
    setSelectedHocKyId(hocKyId);
    onHocKyChange(hocKyId);
  };

  return (
    <>
      {/* Niên khóa */}
      <div className="mr_20">
        <select
          className="form__select w__200"
          value={selectedNienKhoa}
          onChange={(e) => setSelectedNienKhoa(e.target.value)}
          disabled={disabled || loadingHocKy}
        >
          <option value="">-- Chọn Niên khóa --</option>
          {Array.from(new Set(hocKyNienKhoas.map((nk) => nk.tenNienKhoa))).map(
            (tenNK) => (
              <option key={tenNK} value={tenNK}>
                {tenNK}
              </option>
            )
          )}
        </select>
      </div>

      {/* Học kỳ */}
      <div className="mr_20">
        <select
          className="form__select w__200"
          value={selectedHocKyId}
          onChange={(e) => handleHocKyChange(e.target.value)}
          disabled={disabled || !selectedNienKhoa || loadingHocKy}
        >
          <option value="">-- Chọn Học kỳ --</option>
          {filteredHocKys.map((hk) => (
            <option key={hk.id} value={hk.id}>
              {hk.tenHocKy}
            </option>
          ))}
        </select>
      </div>
    </>
  );
}
