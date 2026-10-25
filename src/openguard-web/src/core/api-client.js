import axios from 'axios';

// Phiên đăng nhập nằm trong cookie HttpOnly (JS không đọc được); CSRF token gửi qua header cho mọi yêu cầu ghi.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

let csrfToken = null;
export const setCsrf = (t) => { csrfToken = t; };

api.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase();
  if (csrfToken && !['get', 'head', 'options'].includes(method)) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});

let onUnauthorized = null;
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn; };

api.interceptors.response.use(
  (r) => r,
  (error) => {
    const url = error.config?.url || '';
    if (error.response?.status === 401 && !url.startsWith('/auth/login') && onUnauthorized) onUnauthorized();
    return Promise.reject(error);
  },
);

export function errorText(err, fallback = 'Có lỗi xảy ra, vui lòng thử lại.') {
  const d = err?.response?.data?.detail;
  if (Array.isArray(d)) return d.map((x) => x.msg).join('; ');
  if (typeof d === 'string') return d;
  return err?.message || fallback;
}

export default api;
