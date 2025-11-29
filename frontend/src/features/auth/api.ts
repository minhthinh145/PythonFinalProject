import { api } from "../../app/api";
import type { LoginRequest, LoginResponse } from "./types";

export const authApi = api.injectEndpoints({
  endpoints: (build) => ({
    login: build.mutation<LoginResponse, LoginRequest>({
      query: (body: LoginRequest) => ({
        url: "/api/auth/login",
        method: "POST",
        body
      }),
      // Không cần transformResponse - đã handle ở baseQuery
    }),
  }),
});

export const { useLoginMutation } = authApi;

