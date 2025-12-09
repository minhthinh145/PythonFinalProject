import {
  forwardRef,
  useImperativeHandle,
  useState,
  useEffect,
  type ChangeEvent,
} from "react";
import type {
  KhoaDTO,
  DotGhiDanhResponseDTO,
  UpdateDotGhiDanhRequest,
} from "../../../features/pdt/types/pdtTypes";
import "./KhoaConfigSection.css"; // ✅ Import CSS

export interface KhoaConfig {
  khoaId: string;
  thoiGianBatDau: string;
  thoiGianKetThuc: string;
}

export interface KhoaConfigSectionRef {
  validate: () => boolean;
  getData: () => {
    isToanTruong: boolean;
    dotTheoKhoa: KhoaConfig[];
  };
}

export interface KhoaPhaseConfig {
  id: string;
  khoaIds: string[];
  start: string;
  end: string;
}

interface KhoaConfigSectionProps {
  danhSachKhoa: KhoaDTO[];
  phaseStartTime: string;
  phaseEndTime: string;
  existingDotGhiDanh?: DotGhiDanhResponseDTO[];
  onSubmit: (data: UpdateDotGhiDanhRequest) => Promise<void>; // ✅ Add onSubmit prop
}

export const KhoaConfigSection = forwardRef<
  KhoaConfigSectionRef,
  KhoaConfigSectionProps
>(
  (
    {
      danhSachKhoa,
      phaseStartTime,
      phaseEndTime,
      existingDotGhiDanh = [],
      onSubmit,
    },
    ref
  ) => {
    const [isToanTruong, setIsToanTruong] = useState(true);
    const [khoaConfigs, setKhoaConfigs] = useState<KhoaConfig[]>([]);
    const [isEditMode, setIsEditMode] = useState(false);
    const [validationErrors, setValidationErrors] = useState<string[]>([]);
    const [savedKhoaConfigs, setSavedKhoaConfigs] = useState<KhoaConfig[]>([]);

    useEffect(() => {
      if (existingDotGhiDanh.length === 0) {
        setIsEditMode(true);
        setIsToanTruong(true);
        setKhoaConfigs([]);
        setSavedKhoaConfigs([]);
        return;
      }

      const hasToanTruong = existingDotGhiDanh.some(
        (dot) => dot.isCheckToanTruong
      );

      setIsToanTruong(hasToanTruong);
      setIsEditMode(false);

      if (!hasToanTruong) {
        const configs = existingDotGhiDanh
          .filter((dot) => !dot.isCheckToanTruong && dot.khoaId)
          .map((dot) => ({
            khoaId: dot.khoaId!,
            thoiGianBatDau: new Date(dot.thoiGianBatDau)
              .toISOString()
              .slice(0, 16),
            thoiGianKetThuc: new Date(dot.thoiGianKetThuc)
              .toISOString()
              .slice(0, 16),
          }));

        setKhoaConfigs(configs);
        setSavedKhoaConfigs(configs);
      } else {
        setKhoaConfigs([]);
        setSavedKhoaConfigs([]);
      }
    }, [existingDotGhiDanh]);

    const handleToggleMode = () => {
      if (isEditMode) {
        if (!validate()) {
          return;
        }
      }
      setIsEditMode(!isEditMode);
    };

    const handleAddKhoaConfig = () => {
      setKhoaConfigs([
        ...khoaConfigs,
        {
          khoaId: "",
          thoiGianBatDau: phaseStartTime || "",
          thoiGianKetThuc: phaseEndTime || "",
        },
      ]);
    };

    const handleRemoveKhoaConfig = (index: number) => {
      setKhoaConfigs(khoaConfigs.filter((_, i) => i !== index));
    };

    const handleKhoaConfigChange = (
      index: number,
      field: keyof KhoaConfig,
      value: string
    ) => {
      const newConfigs = [...khoaConfigs];
      newConfigs[index][field] = value;
      setKhoaConfigs(newConfigs);
    };

    const handleToggleToanTruong = (checked: boolean) => {
      if (checked) {
        if (khoaConfigs.length > 0) {
          setSavedKhoaConfigs([...khoaConfigs]);
        }
        setKhoaConfigs([]);
      } else {
        if (savedKhoaConfigs.length > 0) {
          setKhoaConfigs([...savedKhoaConfigs]);
        } else {
          setKhoaConfigs([
            {
              khoaId: "",
              thoiGianBatDau: phaseStartTime || "",
              thoiGianKetThuc: phaseEndTime || "",
            },
          ]);
        }
      }

      setIsToanTruong(checked);
      setValidationErrors([]);
    };

    const validate = (): boolean => {
      const errors: string[] = [];

      if (!isToanTruong) {
        if (khoaConfigs.length === 0) {
          errors.push("Vui lòng thêm ít nhất 1 cấu hình khoa");
        }

        khoaConfigs.forEach((config, index) => {
          if (!config.khoaId) {
            errors.push(`Cấu hình ${index + 1}: Chưa chọn khoa`);
          }
          if (!config.thoiGianBatDau) {
            errors.push(`Cấu hình ${index + 1}: Chưa nhập thời gian bắt đầu`);
          }
          if (!config.thoiGianKetThuc) {
            errors.push(`Cấu hình ${index + 1}: Chưa nhập thời gian kết thúc`);
          }

          if (config.thoiGianBatDau && config.thoiGianKetThuc) {
            if (
              new Date(config.thoiGianBatDau) >=
              new Date(config.thoiGianKetThuc)
            ) {
              errors.push(
                `Cấu hình ${
                  index + 1
                }: Thời gian bắt đầu phải trước thời gian kết thúc`
              );
            }
          }

          if (phaseStartTime && config.thoiGianBatDau) {
            if (new Date(config.thoiGianBatDau) < new Date(phaseStartTime)) {
              errors.push(
                `Cấu hình ${
                  index + 1
                }: Thời gian bắt đầu không được trước thời gian bắt đầu giai đoạn`
              );
            }
          }

          if (phaseEndTime && config.thoiGianKetThuc) {
            if (new Date(config.thoiGianKetThuc) > new Date(phaseEndTime)) {
              errors.push(
                `Cấu hình ${
                  index + 1
                }: Thời gian kết thúc không được sau thời gian kết thúc giai đoạn`
              );
            }
          }
        });

        const khoaIds = khoaConfigs.map((c) => c.khoaId).filter((id) => id);
        const uniqueKhoaIds = new Set(khoaIds);
        if (khoaIds.length !== uniqueKhoaIds.size) {
          errors.push("Không được chọn trùng khoa");
        }
      }

      setValidationErrors(errors);
      return errors.length === 0;
    };

    useImperativeHandle(ref, () => ({
      validate,
      getData: () => ({
        isToanTruong,
        dotTheoKhoa: isToanTruong ? [] : khoaConfigs,
      }),
    }));

    const formatDateTime = (dateString: string) => {
      const date = new Date(dateString);
      return date.toLocaleString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    };

    const renderViewMode = () => {
      if (isToanTruong) {
        const toanTruongDot = existingDotGhiDanh.find(
          (dot) => dot.isCheckToanTruong
        );

        return (
          <div className="khoa-config-view">
            <div className="khoa-config-view__title">
              Cấu hình hiện tại: Toàn trường
            </div>
            {toanTruongDot ? (
              <div className="khoa-config-view__toan-truong">
                <div>
                  <strong>Thời gian bắt đầu:</strong>{" "}
                  {formatDateTime(toanTruongDot.thoiGianBatDau)}
                </div>
                <div>
                  <strong>Thời gian kết thúc:</strong>{" "}
                  {formatDateTime(toanTruongDot.thoiGianKetThuc)}
                </div>
              </div>
            ) : (
              <div className="khoa-config-view__empty">Chưa có cấu hình</div>
            )}
          </div>
        );
      } else {
        const khoaDots = existingDotGhiDanh.filter(
          (dot) => !dot.isCheckToanTruong
        );

        return (
          <div className="khoa-config-view">
            <div className="khoa-config-view__title">
              Cấu hình hiện tại: Riêng từng khoa
            </div>
            {khoaDots.length > 0 ? (
              <div className="khoa-config-view__list">
                {khoaDots.map((dot, index) => (
                  <div key={dot.id} className="khoa-config-view__item">
                    <div className="khoa-config-view__item-name">
                      {index + 1}. {dot.tenKhoa || "N/A"}
                    </div>
                    <div className="khoa-config-view__item-details">
                      <div className="khoa-config-view__item-time">
                        <strong>Bắt đầu:</strong>{" "}
                        {formatDateTime(dot.thoiGianBatDau)}
                      </div>
                      <div className="khoa-config-view__item-time">
                        <strong>Kết thúc:</strong>{" "}
                        {formatDateTime(dot.thoiGianKetThuc)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="khoa-config-view__empty">Chưa có cấu hình</div>
            )}
          </div>
        );
      }
    };

    return (
      <div className="khoa-config-section">
        <div className="khoa-config-header">
          <h4 className="khoa-config-title">Thiết lập đợt ghi danh</h4>
          <button
            type="button"
            onClick={handleToggleMode}
            className={`khoa-config-toggle-btn ${
              isEditMode
                ? "khoa-config-toggle-btn--edit"
                : "khoa-config-toggle-btn--view"
            }`}
          >
            {isEditMode ? "Lưu và xem" : "Chỉnh sửa"}
          </button>
        </div>

        {!isEditMode && renderViewMode()}

        {isEditMode && (
          <>
            <div className="khoa-config-edit__checkbox">
              <label>
                <input
                  type="checkbox"
                  checked={isToanTruong}
                  onChange={(e: ChangeEvent<HTMLInputElement>) =>
                    handleToggleToanTruong(e.target.checked)
                  }
                />
                <span>Áp dụng cho toàn trường</span>
              </label>
            </div>

            {!isToanTruong && (
              <div>
                <div className="khoa-config-list">
                  {khoaConfigs.map((config, index) => (
                    <div key={index} className="khoa-config-item">
                      <div className="khoa-config-item__header">
                        <span className="khoa-config-item__title">
                          Cấu hình {index + 1}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemoveKhoaConfig(index)}
                          className="khoa-config-item__remove-btn"
                        >
                          Xóa
                        </button>
                      </div>

                      <div className="khoa-config-item__fields">
                        <div className="khoa-config-field">
                          <label className="khoa-config-field__label">
                            Khoa:
                          </label>
                          <select
                            value={config.khoaId}
                            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                              handleKhoaConfigChange(
                                index,
                                "khoaId",
                                e.target.value
                              )
                            }
                            className="khoa-config-field__select"
                          >
                            <option value="">-- Chọn khoa --</option>
                            {danhSachKhoa.map((khoa) => (
                              <option key={khoa.id} value={khoa.id}>
                                {khoa.tenKhoa}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div className="khoa-config-field">
                          <label className="khoa-config-field__label">
                            Thời gian bắt đầu:
                          </label>
                          <input
                            type="datetime-local"
                            value={config.thoiGianBatDau}
                            onChange={(e: ChangeEvent<HTMLInputElement>) =>
                              handleKhoaConfigChange(
                                index,
                                "thoiGianBatDau",
                                e.target.value
                              )
                            }
                            min={phaseStartTime}
                            max={config.thoiGianKetThuc || phaseEndTime}
                            className="khoa-config-field__input"
                          />
                        </div>

                        <div className="khoa-config-field">
                          <label className="khoa-config-field__label">
                            Thời gian kết thúc:
                          </label>
                          <input
                            type="datetime-local"
                            value={config.thoiGianKetThuc}
                            onChange={(e: ChangeEvent<HTMLInputElement>) =>
                              handleKhoaConfigChange(
                                index,
                                "thoiGianKetThuc",
                                e.target.value
                              )
                            }
                            min={config.thoiGianBatDau || phaseStartTime}
                            max={phaseEndTime}
                            className="khoa-config-field__input"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={handleAddKhoaConfig}
                  className="khoa-config-add-btn"
                >
                  + Thêm cấu hình cho khoa
                </button>
              </div>
            )}

            {validationErrors.length > 0 && (
              <div className="khoa-config-errors">
                <div className="khoa-config-errors__title">❌ Lỗi:</div>
                <ul className="khoa-config-errors__list">
                  {validationErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    );
  }
);

KhoaConfigSection.displayName = "KhoaConfigSection";
