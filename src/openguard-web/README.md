# OpenGuard Web

Dashboard phụ huynh xây dựng bằng React 19, Vite và React Router. Frontend gọi backend tại `http://localhost:8000/api/v1`.

## Yêu cầu

- Node.js 18 trở lên
- npm
- Backend OpenGuard Server chạy tại cổng `8000`

## Cài đặt và chạy

```powershell
cd src/openguard-web
npm install
npm run dev
```

Mở URL Vite hiển thị trong terminal, thông thường là `http://localhost:5173`.

## Các lệnh khác

```powershell
npm run build     # tạo bản build production trong dist/
npm run preview   # xem thử bản build production
npm run lint      # chạy ESLint
```

## Route hiện có

- Auth: `/login`, `/sign-up`, `/forgot-password`, `/otp`
- Dashboard: `/`
- Trang được bảo vệ: `/time-schedule`, `/sites`, `/chats`, `/tasks`, `/users`, `/settings`

Trang `/reports` có file giao diện trong source nhưng hiện chưa được đăng ký trong `App.jsx`.

## Cấu trúc chính

- `src/App.jsx`: provider, router và protected route
- `src/core/`: API client, authentication context và sidebar context
- `src/features/`: các trang auth và dashboard theo tính năng
- `src/shared/`: Button, Card, Input, Badge, Sidebar và Layout dùng chung
- `public/`: tài nguyên tĩnh

## Kết nối API

`src/core/api-client.js` dùng Axios với `withCredentials: true`, nên server phải cho phép CORS từ `http://localhost:5173`.

Tài khoản mock của server:

```text
Email: parent@openguard.com
Mật khẩu: OpenGuard@2026
```
