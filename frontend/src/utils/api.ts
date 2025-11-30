import axios from "axios";
import { store } from "../app/store";

const api = axios.create({
  // Use /api to go through Vite proxy (Dev) or Nginx proxy (Prod)
  baseURL: import.meta.env.VITE_API_URL || "/api",
});

api.interceptors.request.use((config) => {
  const state = store.getState();
  const token = state.auth.token;
  if (token && !config.url?.includes('login')) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
