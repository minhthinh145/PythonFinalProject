/**
 * Fix broken UTF-8 encoding from backend
 * Backend đang encode sai UTF-8 → Frontend fix lại
 */
export const fixUTF8 = (str: string): string => {
    try {
        // Double-encoded UTF-8 fix
        return decodeURIComponent(escape(str));
    } catch {
        return str; // Fallback if decoding fails
    }
};

/**
 * Parse JWT token and extract user info
 * Handles broken UTF-8 encoding from backend
 */
export const getStudentInfoFromJWT = () => {
    try {
        const token = localStorage.getItem("token");
        if (!token) {
            console.warn("No token found");
            return null;
        }

        const parts = token.split(".");
        if (parts.length !== 3) {
            console.error("Invalid token format");
            return null;
        }

        const payload = JSON.parse(atob(parts[1]));

        return {
            id: payload.sub || "",
            mssv: payload.mssv || payload.ma_so_sinh_vien || "N/A",
            hoTen: fixUTF8(payload.hoTen || payload.ho_ten || payload.name || "N/A"),
            lop: fixUTF8(payload.lop || payload.class || "N/A"),
            nganh: fixUTF8(payload.nganh || payload.nganh_hoc || payload.major || "N/A"),
            role: payload.role || payload.loaiTaiKhoan || "",
        };
    } catch (error) {
        console.error("Error parsing JWT:", error);
        return null;
    }
};
