import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "./store";
import type { ServiceResult } from "../features/common/ServiceResult";

// Base query với transform mặc định unwrap ServiceResult
const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_URL,
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) headers.set("authorization", `Bearer ${token}`);
    return headers;
  },
});

// Transform response: unwrap ServiceResult
const baseQueryWithTransform: typeof baseQuery = async (args, api, extraOptions) => {
  const result = await baseQuery(args, api, extraOptions);

  if (result.data) {
    const serviceResult = result.data as ServiceResult;

    // Nếu success = false, throw error để RTK Query handle
    if (!serviceResult.success) {
      return {
        error: {
          status: result.meta?.response?.status || 400,
          data: serviceResult.message || serviceResult.error || 'Unknown error',
        },
      };
    }

    // Unwrap data từ ServiceResult
    return { ...result, data: serviceResult.data };
  }

  return result;
};

export const api = createApi({
  reducerPath: "api",
  baseQuery: baseQueryWithTransform,
  endpoints: () => ({}),
});
