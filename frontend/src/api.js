/**
 * Axios instance pre-configured with the API base URL.
 * In development the Vite proxy rewrites /api → http://localhost:8000.
 * In production, set VITE_API_URL to the deployed backend URL.
 */
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
