# OpenGuard Server

Backend FastAPI hiện cung cấp xác thực phụ huynh bằng cookie JWT và endpoint heartbeat cho agent.

## Yêu cầu

- Python 3.11 trở lên
- Windows PowerShell hoặc shell tương đương

## Cài đặt

Từ thư mục gốc repository:

```powershell
cd src/openguard-server
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Nếu PowerShell chặn script activate, chạy trực tiếp bằng Python trong môi trường ảo:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Lệnh chạy

```powershell
uvicorn app.main:app --reload --port 8000
```

- Root: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## API hiện có

Tất cả API tính năng dùng tiền tố `/api/v1`:

- `POST /api/v1/auth/login`: đăng nhập bằng cookie `ogk_session`
- `GET /api/v1/auth/me`: lấy thông tin phụ huynh hiện tại
- `POST /api/v1/auth/logout`: xóa cookie phiên
- `POST /api/v1/agent/heartbeat`: nhận heartbeat từ agent

Tài khoản mock:

```text
Email: parent@openguard.com
Mật khẩu: OpenGuard@2026
```

## Cấu hình và kiểm tra

`app/core/config.py` chứa giá trị mặc định cho JWT, CORS và SQLite. Có thể tạo `.env` cạnh `requirements.txt`; `.env.example` hiện là file mẫu trống.

Database mặc định: `sqlite:///./data/ogk_server.db`.

Pytest có trong dependencies, nhưng hiện chưa có test Python trong repository:

```powershell
python -m pytest
```

Các module policy, events, requests, realtime và agent đầy đủ chưa có trong cây tệp hiện tại.
