# AI_USAGE – Khai báo sử dụng AI

> **Nhóm cần tự chỉnh sửa file này** cho đúng quá trình làm việc thực tế của mình (tên thành viên, prompt đã dùng, phần nào tự kiểm chứng). Nội dung dưới đây là bản nháp trung thực về phần do AI sinh ra.

## 1. Công cụ
- Claude (Anthropic), chế độ agent có chạy mã trong sandbox Linux. Dùng để: đọc đề, rà lỗi dự án cũ, viết lại server/agent/dashboard, viết test, viết tài liệu nháp.

## 2. AI đã làm gì
| Hạng mục | Mức độ AI tham gia |
|---|---|
| Server FastAPI (auth, chính sách ký, sự kiện, audit, xóa dữ liệu, WebSocket) | Viết gần như toàn bộ |
| Agent (lõi, DNS proxy, ClockGuard, offline store, AppController) | Viết toàn bộ phần logic; phần Windows (pywin32, PyQt6, netsh, DPAPI) viết nhưng **chưa chạy thật** |
| Dashboard React | Viết lại toàn bộ, thay dữ liệu giả bằng API thật |
| Test (≥15 đơn vị, ≥5 tích hợp) | Viết và chạy trong sandbox |
| PRIVACY / THREATMODEL | Viết nháp |
| Bảng phân loại ≥200 tên miền | Sinh; tên miền "không phù hợp" là tên giả đuôi `.test` |

## 3. Đã kiểm chứng và chưa kiểm chứng
**Đã chạy/kiểm tra:** toàn bộ bộ test (xem `docs/TEST_REPORT.txt`), TLS + ghim chứng chỉ trên localhost, build + lint web, ảnh chụp giao diện desktop/mobile bằng Playwright, đo độ trễ lan truyền chính sách/lệnh khóa trên máy giả lập.

**Chưa kiểm chứng (nhóm phải tự làm):**
- Chạy dịch vụ Windows, tray PyQt6, DPAPI, `netsh` đổi DNS, khóa phiên, DNS proxy cổng 53 trên Windows thật.
- Bắt gói Wireshark, đo hiệu năng thật, thử vượt rào (báo cáo mạng M1–M6).
- **Trích dẫn pháp lý** trong PRIVACY.md: phải đối chiếu lại với văn bản gốc trên các cổng chính thức trước khi nộp.
- Video demo, báo cáo BaoCao.docx và BaoCaoKyThuatMang.pdf do nhóm làm.

## 4. Nhật ký quyết định (điền/sửa)
| Ngày | Nội dung hỏi AI | Kết quả | Nhóm đã kiểm tra/sửa gì |
|---|---|---|---|
| | Rà lỗi dự án cũ | Danh sách lỗi (mã chết, lỗi múi giờ, heartbeat 5 s, v.v.) | |
| | Thiết kế offline fail-safe | Chọn "dùng chính sách ký đã lưu, quá 7 ngày dùng mặc định" | |
| | | | |

## 5. Cam kết
Không dùng AI để đọc nội dung tin nhắn/tài liệu của trẻ; không thử nghiệm trên trẻ em thật hoặc máy người khác khi chưa đồng ý; dữ liệu thử là tên miền công khai, trung lập.
