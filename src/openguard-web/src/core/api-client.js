import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Danh sách các route công khai thuộc nhóm xác thực không bị cưỡng chế redirect khi gặp 401
const AUTH_ROUTES = ['/login', '/sign-in', '/sign-up', '/forgot-password', '/otp'];

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const currentPath = window.location.pathname;
      const isAuthRoute = AUTH_ROUTES.some((route) => currentPath.startsWith(route));

      // Chỉ redirect về /login nếu người dùng đang cố truy cập các trang nội bộ (như / hoặc /dashboard)
      if (!isAuthRoute) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
