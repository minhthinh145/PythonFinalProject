/**
 * ServiceResult - Standard API response wrapper
 * Map 1-1 với backend ServiceResult
 */
export interface ServiceResult<T = any> {
    success: boolean;  // Map với BE success field
    message: string;
    data?: T;
    error?: string;
}
