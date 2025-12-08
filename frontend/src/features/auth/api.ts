import { api } from "../../app/api";
import type { LoginRequest, LoginResponse } from "./types";

import type { ServiceResult } from "../common/ServiceResult";

export const authApi = api.injectEndpoints({
  endpoints: (build) => ({
    login: build.mutation<ServiceResult<LoginResponse>, LoginRequest>({
      query: (body: LoginRequest) => ({
        url: "auth/login",
        method: "POST",
        body
      }),
      // Không cần transformResponse - đã handle ở baseQuery
    }),
  }),
});

export const { useLoginMutation } = authApi;

