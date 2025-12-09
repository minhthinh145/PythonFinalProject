import { useState } from "react";
import type { GVDocumentDTO } from "../../../features/gv/api/gvLopHocPhanAPI";
import { gvLopHocPhanAPI } from "../../../features/gv/api/gvLopHocPhanAPI";
import TaiLieuPreviewModal from "./TaiLieuPreviewModal";
import "../../../styles/tailieu-list.css";

interface Props {
  documents: GVDocumentDTO[];
  onDelete: (docId: string) => void;
  onGetUrl: (docId: string) => Promise<string | null>;
  submitting: boolean;
  lhpId: string; // ✅ Add lhpId
}

export default function TaiLieuList({
  documents,
  onDelete,
  onGetUrl,
  submitting,
  lhpId,
}: Props) {
  const [previewDoc, setPreviewDoc] = useState<GVDocumentDTO | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loadingUrl, setLoadingUrl] = useState(false);

  // ✅ Check if file can be previewed based on file_type
  const canPreview = (doc: GVDocumentDTO) => {
    const previewableTypes = [
      "application/pdf",
      "image/jpeg",
      "image/jpg",
      "image/png",
    ];
    return doc.file_type && previewableTypes.includes(doc.file_type);
  };

  // ✅ Get file icon based on file_type
  const getFileIcon = (doc: GVDocumentDTO) => {
    const type = doc.file_type?.toLowerCase() || "";

    if (type.includes("pdf")) return "📄";
    if (type.includes("word") || type.includes("msword")) return "📝";
    if (type.includes("powerpoint") || type.includes("presentation"))
      return "📊";
    if (type.includes("text")) return "📃";
    if (type.includes("video")) return "🎥";
    if (type.includes("image")) return "🖼️";
    if (type.includes("zip") || type.includes("compressed")) return "📦";

    return "📎";
  };

  const handlePreview = async (doc: GVDocumentDTO) => {
    setLoadingUrl(true);
    const url = await onGetUrl(doc.id);
    setLoadingUrl(false);

    if (url) {
      setPreviewDoc(doc);
      setPreviewUrl(url);
    }
  };

  const handleDownload = async (doc: GVDocumentDTO) => {
    try {
      // ✅ Download via backend proxy
      const blob = await gvLopHocPhanAPI.downloadTaiLieu(lhpId, doc.id);

      if (blob) {
        // ✅ Create download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = doc.ten_tai_lieu;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Error downloading:", error);
    }
  };

  // ✅ Cleanup blob URLs
  const handleClosePreview = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewDoc(null);
    setPreviewUrl(null);
  };

  return (
    <>
      <div className="tailieu-list">
        {documents.length === 0 && (
          <div className="tailieu-empty">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z"
                fill="#94A3B8"
              />
            </svg>
            <p>Chưa có tài liệu nào</p>
          </div>
        )}

        {documents.map((doc) => (
          <div key={doc.id} className="tailieu-item">
            <div className="tailieu-icon">{getFileIcon(doc)}</div>

            <div className="tailieu-info">
              <div className="tailieu-name">{doc.ten_tai_lieu}</div>
              <div className="tailieu-meta">
                {doc.created_at &&
                  new Date(doc.created_at).toLocaleDateString("vi-VN")}
                {doc.file_type && (
                  <span className="tailieu-type">
                    {" • "}
                    {doc.file_type.split("/")[1]?.toUpperCase() || "FILE"}
                  </span>
                )}
              </div>
            </div>

            <div className="tailieu-actions">
              {canPreview(doc) && (
                <button
                  className="btn-preview"
                  onClick={() => handlePreview(doc)}
                  disabled={loadingUrl}
                  title="Xem trước"
                >
                  {loadingUrl ? (
                    // Icon đồng hồ cát (loading)
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 384 512"
                      width={18}
                      height={18}
                      aria-hidden="true"
                    >
                      <path
                        fill="#d39b32ff"
                        d="M32 0C14.3 0 0 14.3 0 32S14.3 64 32 64l0 11c0 42.4 16.9 83.1 46.9 113.1l67.9 67.9-67.9 67.9C48.9 353.9 32 394.6 32 437l0 11c-17.7 0-32 14.3-32 32s14.3 32 32 32l320 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l0-11c0-42.4-16.9-83.1-46.9-113.1l-67.9-67.9 67.9-67.9c30-30 46.9-70.7 46.9-113.1l0-11c17.7 0 32-14.3 32-32S369.7 0 352 0L32 0zM96 75l0-11 192 0 0 11c0 19-5.6 37.4-16 53L112 128c-10.3-15.6-16-34-16-53zm16 309c3.5-5.3 7.6-10.3 12.1-14.9l67.9-67.9 67.9 67.9c4.6 4.6 8.6 9.6 12.2 14.9L112 384z"
                      />
                    </svg>
                  ) : (
                    // Icon con mắt (preview)
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 640 640"
                      width={18}
                      height={18}
                      aria-hidden="true"
                    >
                      <path
                        fill="#0c4874"
                        d="M320 96C239.2 96 174.5 132.8 127.4 176.6C80.6 220.1 49.3 272 34.4 307.7C31.1 315.6 31.1 324.4 34.4 332.3C49.3 368 80.6 420 127.4 463.4C174.5 507.1 239.2 544 320 544C400.8 544 465.5 507.2 512.6 463.4C559.4 419.9 590.7 368 605.6 332.3C608.9 324.4 608.9 315.6 605.6 307.7C590.7 272 559.4 220 512.6 176.6C465.5 132.9 400.8 96 320 96zM176 320C176 240.5 240.5 176 320 176C399.5 176 464 240.5 464 320C464 399.5 399.5 464 320 464C240.5 464 176 399.5 176 320zM320 256C320 291.3 291.3 320 256 320C244.5 320 233.7 317 224.3 311.6C223.3 322.5 224.2 333.7 227.2 344.8C240.9 396 293.6 426.4 344.8 412.7C396 399 426.4 346.3 412.7 295.1C400.5 249.4 357.2 220.3 311.6 224.3C316.9 233.6 320 244.4 320 256z"
                      />
                    </svg>
                  )}
                </button>
              )}

              <button
                className="btn-download"
                onClick={() => handleDownload(doc)}
                disabled={loadingUrl}
                title="Tải xuống"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                  <path
                    fill="#0c4874"
                    d="M256 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 210.7-41.4-41.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l96 96c12.5 12.5 32.8 12.5 45.3 0l96-96c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 242.7 256 32zM64 320c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-46.9 0-56.6 56.6c-31.2 31.2-81.9 31.2-113.1 0L110.9 320 64 320zm304 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"
                  />
                </svg>
              </button>

              <button
                className="btn-delete"
                onClick={() => onDelete(doc.id)}
                disabled={submitting}
                title="Xóa"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                  <path
                    fill="#cf373d"
                    d="M136.7 5.9L128 32 32 32C14.3 32 0 46.3 0 64S14.3 96 32 96l384 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0-8.7-26.1C306.9-7.2 294.7-16 280.9-16L167.1-16c-13.8 0-26 8.8-30.4 21.9zM416 144L32 144 53.1 467.1C54.7 492.4 75.7 512 101 512L347 512c25.3 0 46.3-19.6 47.9-44.9L416 144z"
                  />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>

      {previewDoc && previewUrl && (
        <TaiLieuPreviewModal
          document={previewDoc}
          fileUrl={previewUrl}
          onClose={handleClosePreview}
        />
      )}
    </>
  );
}
