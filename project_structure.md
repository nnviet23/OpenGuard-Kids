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
    ├── openguard-web/
    │   ├── .gitignore
    │   ├── README.md
    │   ├── eslint.config.js
    │   ├── index.html
    │   ├── package.json
    │   ├── package-lock.json
    │   ├── postcss.config.js
    │   ├── vite.config.js
    │   ├── public/
    │   │   ├── favicon.svg
    │   │   └── icons.svg
    │   └── src/
    │       ├── App.jsx
    │       ├── global.css
    │       ├── index.css
    │       ├── main.jsx
    │       ├── tailwind.config.js
    │       ├── assets/
    │       │   ├── hero.png
    │       │   ├── react.svg
    │       │   └── vite.svg
    │       ├── core/
    │       │   ├── api-client.js
    │       │   ├── AuthContext.jsx
    │       │   └── SidebarContext.jsx
    │       ├── features/
    │       │   ├── auth/
    │       │   │   ├── auth-layout.jsx + auth-layout.module.css
    │       │   │   ├── forgot-password/index.jsx + forgot-password.module.css
    │       │   │   ├── otp/index.jsx + otp.module.css
    │       │   │   ├── sign-in/index.jsx + sign-in.module.css
    │       │   │   ├── sign-in/components/user-auth-form.jsx
    │       │   │   └── sign-up/index.jsx + sign-up.module.css
    │       │   ├── chats/page.jsx + chats.module.css
    │       │   ├── dashboard/page.jsx + dashboard.module.css
    │       │   ├── reports/page.jsx + reports.module.css
    │       │   ├── settings/page.jsx + settings.module.css
    │       │   ├── sites/page.jsx + sites.module.css
    │       │   ├── tasks/page.jsx + tasks.module.css
    │       │   ├── time-schedule/page.jsx + time.module.css
    │       │   └── users/page.jsx + users.module.css
    │       └── shared/
    │           ├── index.js
    │           ├── Badge/Badge.jsx + Badge.module.css
    │           ├── Button/Button.jsx + Button.module.css
    │           ├── Card/Card.jsx + Card.module.css
    │           ├── Input/Input.jsx + Input.module.css
    │           ├── Layout/DashboardLayout.jsx
    │           ├── Layout/TopHeader.jsx + TopHeader.module.css
    │           └── Sidebar/Sidebar.jsx + Sidebar.module.css
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
