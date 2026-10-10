# OpenGuard Kids (OGK)

> **"Công cụ đồng hành, không phải phần mềm theo dõi lén"**  
> Hệ thống hỗ trợ phụ huynh quản lý thời gian và môi trường sử dụng máy tính của trẻ em trên Windows 10/11, tuân thủ nguyên tắc tối thiểu dữ liệu và minh bạch hai chiều.

---

## 📌 Mục lục

- [Giới thiệu & Triết lý Thiết kế](#-giới-thiệu--triết-lý-thiết-kế)
- [Cấu trúc Thư mục Dự án](#-cấu-trúc-thư-mục-dự-án)
- [Yêu cầu Tiên quyết](#-yêu-cầu-tiên-quyết)
- [Hướng dẫn Cài đặt & Chạy Thử (Dưới 15 Phút)](#-hướng-dẫn-cài-đặt--chạy-thử-dưới-15-phút)
  - [1. Khởi động Backend (FastAPI)](#1-khởi-động-backend-openguard-server)
  - [2. Khởi động Frontend Dashboard (React + Vite)](#2-khởi-động-dashboard-openguard-web)
  - [3. Cài đặt & Chạy Agent (Windows 10/11)](#3-cài-đặt--chạy-agent-openguard-agent)
- [Tài khoản Demo & Kiểm thử](#-tài-khoản-demo--kiểm-thử)
- [Tài liệu Liên quan](#-tài-liệu-liên-quan)

---

## 🌟 Giới thiệu & Triết lý Thiết kế

OpenGuard Kids được xây dựng dựa trên các chuẩn mực an toàn số (NIST SP 800-63B, OWASP ASVS v4) và khung pháp lý Việt Nam (Luật Trẻ em 2016, Nghị định 13/2023/NĐ-CP):

1. **Minh bạch với trẻ (NT1):** Biểu tượng khay hệ thống luôn thường trực; không có chế độ chạy ẩn, không phải phần mềm gián điệp.
2. **Tối thiểu dữ liệu (NT2):** Chỉ lưu trữ siêu dữ liệu sử dụng (tên ứng dụng, tên miền cấp 2, thời lượng). **Không** lưu URL đầy đủ, phím bấm (keylogger), ảnh chụp màn hình hay đọc tin nhắn.
3. **Tiếng nói hai chiều (NT3, NT5):** Cung cấp nút *“Xin thêm giờ”*, *“Báo chặn nhầm”* và màn hình *“Hôm nay em đã dùng gì”* để trẻ cùng theo dõi hoạt động với phụ huynh.
4. **Hàng rào kỹ thuật vững chắc:** Kết hợp DNS Proxy cục bộ (127.0.0.1:53) vô hiệu hóa DoH qua Canary Domain, cưỡng chế SafeSearch và kiểm soát ứng dụng theo mã băm SHA-256.

---

## 📂 Cấu trúc Thư mục Dự án

```text
OpenGuardKid/
├── docs/                     # Tài liệu pháp lý và kỹ thuật (PRIVACY.md, THREATMODEL.md,...)
├── src/
│   ├── openguard-server/     # Backend FastAPI (Kiến trúc Feature-based, SQLite WAL)
│   ├── openguard-web/        # Dashboard Phụ huynh (React + Vite + Tailwind CSS)
│   └── openguard-agent/      # Agent Windows (Service SYSTEM + Tray UI User Session)
├── docker-compose.yml        # Triển khai nhanh Server & Web bằng Docker
└── README.md
```

### Chi tiết các phân hệ:
* **`openguard-server/`**: Cung cấp API RESTful & kênh WebSocket thời gian thực (`/ws/commands`), xác thực phụ huynh (Argon2id), cấp phát token JWT và đồng bộ chính sách (chữ ký HMAC-SHA256).
* **`openguard-web/`**: Dashboard quản trị di động/desktop cho phụ huynh: ma trận lịch tuần $7\times48$, thanh trượt quota ngày, danh mục chặn tên miền và duyệt yêu cầu của trẻ.
* **`openguard-agent/`**: Tác tử máy trạm Windows chia làm 2 thành phần độc lập:
  * `main_service.py`: Dịch vụ nền chạy quyền `NT AUTHORITY\SYSTEM` (đếm giờ bằng `time.monotonic()`, DNS Proxy cổng 53, kiểm soát tiến trình `psutil` theo SHA-256).
  * `main_ui.py`: Giao diện khay hệ thống chạy trong phiên người dùng (User Session), giao tiếp với Service qua Named Pipe (IPC) có mã xác thực Local Token 128-bit.

---

## 💻 Yêu cầu Tiên quyết

- **Máy chủ / Dashboard:**
  - Python 3.11+
  - Node.js 18+ & npm
  - (Tùy chọn) Docker & Docker Compose
- **Máy trạm của trẻ (Agent):**
  - Windows 10/11 x64 (Clean VM hoặc máy thật)
  - Quyền Quản trị viên (Administrator) cho thao tác cài đặt ban đầu

---

## 🚀 Hướng dẫn Cài đặt & Chạy Thử (Dưới 15 Phút)

### 1. Khởi động Backend (`openguard-server`)

```bash
cd src/openguard-server

# Tạo môi trường ảo và cài đặt thư viện
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt

# Khởi chạy máy chủ phát triển
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
> API Docs khả dụng tại: `http://localhost:8000/docs`

---

### 2. Khởi động Dashboard (`openguard-web`)

Mở terminal mới:

```bash
cd src/openguard-web

# Cài đặt dependencies
npm install

# Khởi chạy frontend Vite
npm run dev
```
> Bảng điều khiển phụ huynh khả dụng tại: `http://localhost:5173`

---

### 3. Cài đặt & Chạy Agent (`openguard-agent`)

Thực hiện trên máy tính Windows:

```powershell
cd src/openguard-agent

# Tạo môi trường ảo
python -m venv venv
.\venv\Scripts\activate

# Cài đặt thư viện cần thiết
pip install -r requirements.txt
```

#### Bước A: Khởi chạy Windows Service (quyền SYSTEM / Admin)
Mở PowerShell bằng quyền **Run as Administrator**:
```powershell
python src/main_service.py
```
*Dịch vụ sẽ tự động mở DNS Proxy tại `127.0.0.1:53`, thiết lập Named Pipe Server và giám sát tiến trình.*

#### Bước B: Khởi chạy Tray UI (User Session)
Mở một cửa sổ dòng lệnh bình thường (phiên của trẻ):
```powershell
python src/main_ui.py
```
*Biểu tượng OpenGuard Kids sẽ xuất hiện tại khay hệ thống góc dưới bên phải màn hình.*

---

## 🔑 Tài khoản Demo & Kiểm thử

Khi khởi động server lần đầu, dữ liệu seed mẫu được tạo sẵn phục vụ việc chấm điểm:

| Thông tin | Giá trị |
| :--- | :--- |
| **URL Đăng nhập** | `http://localhost:5173/login` |
| **Tài khoản phụ huynh** | `parent@openguard.local` |
| **Mật khẩu** | `OpenGuard@2026` |
| **Mã Ghép đôi (Enrollment Code)** | Tạo ngẫu nhiên 8 ký tự trên Dashboard (Hạn 10 phút) |

### Các kịch bản kiểm thử nhanh:
1. **Kiểm tra lọc DNS & SafeSearch:** Mở trình duyệt trên máy Agent, truy cập một tên miền trong danh sách cấm hoặc tìm kiếm trên Google/YouTube để kiểm tra cưỡng chế SafeSearch.
2. **Kiểm tra đổi tên file (.exe):** Đổi tên một file game bị chặn thành `notepad.exe` và khởi chạy — Agent sẽ phát hiện mã băm SHA-256 và cưỡng chế tắt trong vòng 1 giây.
3. **Lệnh khẩn WebSocket:** Nhấn nút *"Khóa máy ngay"* trên Dashboard — Máy Agent sẽ kích hoạt `LockWorkStation` trong vòng dưới 5 giây.

---

## 📚 Tài liệu Liên quan

- [`/docs/PRIVACY.md`](docs/PRIVACY.md): Bảng quy chuẩn tối thiểu hóa dữ liệu (kèm phiên bản dành riêng cho trẻ em).
- [`/docs/THREATMODEL.md`](docs/THREATMODEL.md): Mô hình mối đe dọa STRIDE và checklist tự đánh giá OWASP ASVS v4.
- [`/docs/BaoCaoKyThuatMang.pdf`](docs/BaoCaoKyThuatMang.pdf): Báo cáo đào sâu kỹ thuật mạng M1 - M6.
- [`/docs/AI_USAGE.md`](docs/AI_USAGE.md): Khai báo việc ứng dụng các công cụ AI trong đồ án.