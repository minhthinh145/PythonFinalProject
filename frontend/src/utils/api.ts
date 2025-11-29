import axios from "axios";
import { store } from "../app/store";

const api = axios.create({
  // Use relative path for production (nginx proxy), localhost for dev
  baseURL: import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://localhost:8000" : ""),
});

api.interceptors.request.use((config) => {
  const state = store.getState();
  const token = state.auth.token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
