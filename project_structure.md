# OpenGuardKid - Cấu trúc dự án

Tài liệu này mô tả cây tệp hiện có trong repository. Các thư mục hoặc tính năng chưa tồn tại không được liệt kê như đã triển khai.

## Cây thư mục

```text
OpenGuardKid/
├── README.md
├── project_structure.md
└── src/
    ├── docs/
    │   ├── AI_USAGE.md
    │   ├── PRIVACY.md
    │   └── THREATMODEL.md
    ├── openguard-server/
    │   ├── .env.example
    │   ├── README.md
    │   ├── requirements.txt
    │   └── app/
    │       ├── __init__.py
    │       ├── main.py
    │       ├── core/
    │       │   ├── __init__.py
    │       │   ├── config.py
    │       │   ├── database.py
    │       │   ├── dependencies.py
    │       │   └── security.py
    │       └── features/
    │           ├── auth/
    │           │   ├── router.py
    │           │   └── schemas.py
    │           └── devices/
    │               ├── router.py
    │               └── schemas.py
        openguard-web/
        ├── index.html
        ├── package.json
        ├── vite.config.js
        ├── public/
        │   └── favicon.svg
        └── src/
            ├── main.jsx                     # Điểm khởi chạy React (ReactDOM.createRoot)
            ├── App.jsx                      # Cấu hình Router (0_auth -> 7_settings)
            │
            ├── styles/                      # Hệ thống style tập trung (Không Tailwind)
            │   ├── tokens.css               # Color tokens, fonts, variables đã tạo
            │   └── global.css               # Reset CSS, typography, layout chung
            │
            ├── context/                     # Quản lý State toàn cục
            │   ├── AuthContext.jsx          # Trạng thái đăng nhập phụ huynh, phiên 12h
            │   └── ChildContext.jsx         # Trẻ/Thiết bị đang chọn (Bé Nam Việt / Bé Mai Anh)
            │
            ├── services/                    # Tầng giao tiếp Backend FastAPI
            │   ├── api.js                   # Wrapper fetch/axios (Credentials, Cookie HttpOnly)
            │   └── websocket.js             # Kết nối WebSocket lệnh khẩn (/ws/commands)
            │
            ├── components/                  # Thành phần dùng chung (Shared UI)
            │   ├── layout/
            │   │   ├── DashboardLayout.jsx  # Khung bọc gồm Sidebar + Topbar + Main
            │   │   ├── Sidebar.jsx          # Thanh điều hướng 7 trang
            │   │   ├── Topbar.jsx           # Header chọn trẻ & thông tin phụ huynh
            │   │   └── EmergencyBar.jsx     # Thanh lệnh khẩn (Khóa, Mở, +15p)
            │   ├── common/
            │   │   ├── Badge.jsx            # Nhãn trạng thái sắc cạnh (badge-mono)
            │   │   ├── Button.jsx           # Nút bấm phong cách pixel/crisp
            │   │   ├── Card.jsx             # Khung thẻ nội dung (card-box)
            │   │   └── Modal.jsx            # Hộp thoại popup dùng chung
            │   └── icons/
            │       └── PixelIcons.jsx       # Toàn bộ bộ icon 2D SVG monochrome
            │
            └── features/                    # 8 Phân hệ chức năng chính
                ├── 0_auth/                  # Đăng nhập, Quên mật khẩu, Xác thực 2FA OTP
                │   ├── LoginPage.jsx
                │   └── ForgotPasswordPage.jsx
                ├── 1_overview/              # Trang 1: Tổng quan, 4 KPI, Top Domain, Top App
                │   ├── OverviewPage.jsx
                │   ├── components/WeeklyBarChart.jsx
                │   └── components/CategoryDonutChart.jsx
                ├── 2_schedule/              # Trang 2: Lịch tuần (Ma trận 7x48, Quota ngày)
                │   ├── SchedulePage.jsx
                │   └── components/TimeMatrix7x48.jsx
                ├── 3_requests/              # Trang 3: Yêu cầu từ trẻ (Duyệt 1 chạm, gửi lời nhắn)
                │   ├── RequestsPage.jsx
                │   └── components/DecisionModal.jsx
                ├── 4_apps/                  # Trang 4: Ứng dụng & Web (DNS, SHA-256, Danh mục)
                │   ├── AppsPage.jsx
                │   └── components/AddRuleModal.jsx
                ├── 5_reports/               # Trang 5: Báo cáo, Sum theo nhóm, Xuất CSV/PDF
                │   ├── ReportsPage.jsx
                │   └── components/EyeBreakWidget.jsx
                ├── 6_audit/                 # Trang 6: Nhật ký kiểm toán, Quyền xóa dữ liệu NĐ 13
                │   ├── AuditPage.jsx
                │   └── components/EraseDataModal.jsx
                └── 7_settings/              # Trang 7: Mật khẩu Argon2id, TOTP, Quản lý thiết bị
                    ├── SettingsPage.jsx
                    └── components/DeviceList.jsx
    ├── openguard-agent/
    │   ├── requirements.txt
    │   └── src/
    │       ├── main_service.py
    │       └── main_ui.py
    └── tests/
        └── datasets/
            ├── sample_policies.json
            └── test_domains_50.txt
```

`+` trong cây trên gộp hai tệp cùng thư mục để tài liệu ngắn gọn; cả hai tệp đều tồn tại.

## Vai trò các phần chính

- `src/openguard-server`: API FastAPI. Hiện có xác thực phụ huynh bằng cookie JWT và endpoint heartbeat cho agent. Dữ liệu mặc định dùng SQLite.
- `src/openguard-web`: Dashboard React/Vite. `App.jsx` đăng ký các trang xác thực và dashboard; client API mặc định gọi `http://localhost:8000/api/v1`.
- `src/openguard-agent`: Khung entry point cho service và UI Windows. Hai file hiện đang là placeholder, chưa có logic agent.
- `src/docs`: Tài liệu quyền riêng tư, threat model và khai báo sử dụng AI.
- `src/tests/datasets`: Dữ liệu mẫu; hiện chưa có test tự động trong repository.

## Chạy cục bộ

```powershell
cd src/openguard-server
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```powershell
cd src/openguard-web
npm install
npm run dev
```

- Server: `http://localhost:8000`, OpenAPI: `http://localhost:8000/docs`
- Web: URL Vite hiển thị trong terminal, mặc định thường là `http://localhost:5173`
