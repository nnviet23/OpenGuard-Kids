# OpenGuard Kids – hỗ trợ quản lý việc dùng máy tính của trẻ em

Hệ thống minh bạch, đặt trẻ em làm trung tâm: **agent Windows** (dịch vụ + biểu tượng khay luôn hiển thị) – **server FastAPI + SQLite** – **dashboard React** dùng được trên điện thoại.

| Theo đề bài | Thư mục |
|---|---|
| /agent | `src/openguard-agent` |
| /server | `src/openguard-server` |
| /dashboard | `src/openguard-web` |
| /tests | `src/tests` |
| /docs | `docs/` (PRIVACY.md, THREATMODEL.md, AI_USAGE.md, BaoCaoKyThuatMang/, TEST_REPORT.txt) |
| công cụ đo | `tools/` |

## Cài đặt trong ~15 phút

### 1. Server (Linux/macOS/Windows, Python 3.11+)
```bash
cd src/openguard-server
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # dev: có thể để trống OGK_MASTER_KEY
```
### 2. Dashboard
```bash
cd src/openguard-web
npm install && npm run build        # server tự phục vụ thư mục dist
```
### 3. Chạy
```bash
cd src/openguard-server
python -m uvicorn app.main:app --port 8000
```
Mở http://127.0.0.1:8000 . Tài khoản demo (chỉ khi `OGK_SEED_DEMO=true`):
- Phụ huynh: `parent@example.com` / `OpenGuard@2026`
- Bé xem (child_view): `beminh@example.com` / `BeMinh@2026`
- Quản trị: `admin@example.com` (mật khẩu xem `seed.py`; admin **không** đọc được dữ liệu của trẻ)

Dev nhanh dashboard: `npm run dev` (proxy `/api` → cổng 8000). Production: đặt `OGK_ENV=prod`, `OGK_MASTER_KEY` ≥32 ký tự, `OGK_COOKIE_SECURE=true`, chạy sau TLS (`scripts/make_dev_cert.py` tạo chứng chỉ thử).

### 4. Agent trên Windows (máy thử nghiệm của chính nhóm)
```powershell
cd src\openguard-agent
powershell -ExecutionPolicy Bypass -File install_agent.ps1 -Server http://<ip-server>:8000/api/v1
```
Trên dashboard: Gia đình → tạo mã ghép cặp (8 ký tự, hiệu lực 10 phút, phải tích xác nhận đã đồng ý/đã thông báo cho trẻ) → chạy:
```powershell
python src\main_service.py enroll --code ABCD2345 --name "Máy thử"
python src\main_service.py run          # hoặc: service install / start
python src\main_ui.py                   # biểu tượng khay
```

### Chế độ thực thi (mặc định **chỉ ghi nhận – dry-run**)
| Biến | Tác dụng |
|---|---|
| `OPENGUARD_ENFORCE_LOCK=1` | khóa phiên Windows khi hết giờ |
| `OPENGUARD_ENFORCE_APPS=1` | tắt ứng dụng bị chặn |
| `OPENGUARD_MANAGE_DNS=1` | bật DNS proxy và đổi DNS hệ thống (cần quyền quản trị) |

⚠️ Chỉ bật trên **tài khoản/máy thử nghiệm của nhóm**, có sự đồng ý. Không thử trên trẻ thật hay máy người khác. Xem `src/openguard-agent/ENFORCEMENT_TESTING.md`.

## Kiểm thử
```bash
cd src && python -m pytest tests -q        # 15+ test đơn vị, 5+ tích hợp (kết quả: docs/TEST_REPORT.txt)
```

## Nguyên tắc & tài liệu
NT1–NT6 (icon khay luôn hiện, tối thiểu hóa dữ liệu, trẻ gửi yêu cầu/khiếu nại, mọi chặn đều có lý do, minh bạch hai chiều, danh sách an toàn vĩnh viễn) – xem `docs/PRIVACY.md`, `docs/THREATMODEL.md`. Không đọc nội dung tin nhắn/tài liệu, không ẩn tiến trình, không chống gỡ cài đặt (gỡ sẽ báo cho phụ huynh).

## Hạn chế đã biết
Phần chỉ chạy trên Windows (dịch vụ pywin32, tray PyQt6, DPAPI, netsh, khóa phiên) được viết nhưng chưa chạy thử trong môi trường phát triển Linux; số liệu Wireshark/hiệu năng thật nhóm cần tự đo (xem `docs/BaoCaoKyThuatMang/README.md`).
