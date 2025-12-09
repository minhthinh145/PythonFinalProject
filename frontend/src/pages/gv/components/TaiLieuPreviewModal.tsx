import { useState } from "react";
import type { GVDocumentDTO } from "../../../features/gv/api/gvLopHocPhanAPI";
import "../../../styles/tailieu-preview.css";

interface Props {
  document: GVDocumentDTO;
  fileUrl: string; // ✅ Presigned URL from S3
  onClose: () => void;
}

export default function TaiLieuPreviewModal({
  document,
  fileUrl,
  onClose,
}: Props) {
  const [iframeError, setIframeError] = useState(false);
  const [imageError, setImageError] = useState(false);

  // ✅ Detect file type from MIME type (file_type field from DB)
  const fileType = document.file_type?.toLowerCase() || "";

  const isPDF = fileType.includes("pdf");
  const isImage = fileType.includes("image");
  const isDoc = fileType.includes("word") || fileType.includes("msword");

  return (
    <div className="preview-overlay" onClick={onClose}>
      <div className="preview-container" onClick={(e) => e.stopPropagation()}>
        <div className="preview-header">
          <h3>{document.ten_tai_lieu}</h3>
          <button className="preview-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="preview-body">
          {/* ✅ PDF Preview */}
          {isPDF && !iframeError && (
            <iframe
              src={`${fileUrl}#toolbar=0`}
              title={document.ten_tai_lieu}
              className="preview-iframe"
              onError={() => {
                console.error("❌ Iframe failed to load PDF");
                setIframeError(true);
              }}
            />
          )}

          {/* ✅ Image Preview */}
          {isImage && !imageError && (
            <img
              src={fileUrl} // ✅ Use presigned URL
              alt={document.ten_tai_lieu}
              className="preview-image"
              onError={() => {
                console.error("❌ Image failed to load");
                setImageError(true);
              }}
            />
          )}

          {/* ✅ Word documents - không preview được, chỉ download */}
          {isDoc && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                gap: "16px",
              }}
            >
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z"
                  fill="#2563eb"
                />
              </svg>
              <p style={{ color: "#6b7280", fontWeight: 600 }}>
                📝 File Word không hỗ trợ xem trước
              </p>
              <p style={{ fontSize: "14px", color: "#9ca3af" }}>
                Vui lòng tải xuống để xem
              </p>
            </div>
          )}

          {/* ✅ Error fallback */}
          {((isPDF && iframeError) || (isImage && imageError)) && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                gap: "16px",
              }}
            >
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z"
                  fill="#dc2626"
                />
              </svg>
              <p style={{ color: "#dc2626", fontWeight: 600 }}>
                ⚠️ Không thể xem trước file
              </p>
              <p style={{ fontSize: "14px", color: "#6b7280" }}>
                Vui lòng tải xuống để xem
              </p>
            </div>
          )}

          {/* ✅ Fallback nếu không phải PDF/Image/Doc */}
          {!isPDF && !isImage && !isDoc && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                gap: "16px",
              }}
            >
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2ZM18 20H6V4H13V9H18V20Z"
                  fill="#6b7280"
                />
              </svg>
              <p style={{ color: "#6b7280", fontWeight: 600 }}>
                📎 File {document.file_type || "này"} không hỗ trợ xem trước
              </p>
              <p style={{ fontSize: "14px", color: "#9ca3af" }}>
                Vui lòng tải xuống để xem
              </p>
            </div>
          )}
        </div>

        <div className="preview-footer">
          <a
            href={fileUrl} // ✅ Use presigned URL
            download={document.ten_tai_lieu}
            className="btn__chung"
            target="_blank"
            rel="noopener noreferrer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
              <path
                fill="#ffffffff"
                d="M256 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 210.7-41.4-41.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l96 96c12.5 12.5 32.8 12.5 45.3 0l96-96c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L256 242.7 256 32zM64 320c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-46.9 0-56.6 56.6c-31.2 31.2-81.9 31.2-113.1 0L110.9 320 64 320zm304 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"
              />
            </svg>{" "}
            Tải xuống
          </a>
        </div>
      </div>
    </div>
  );
}
