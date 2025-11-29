/**
 * ServiceResult - Standard API response wrapper
 * Map 1-1 với backend ServiceResult
 */
export interface ServiceResult<T = any> {
    isSuccess: boolean;  // Map với BE isSuccess field
    message: string;
    data?: T;
    error?: string;
}
