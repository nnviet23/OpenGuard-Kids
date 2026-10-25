# OpenGuard Kids — Chính sách quyền riêng tư & bảo vệ dữ liệu

> Phiên bản 1.1 · áp dụng cho OGK-Agent, OGK-Server và OGK-Dashboard.
> Bản dành cho trẻ em (ngôn ngữ đơn giản): [`PRIVACY_TRE_EM.md`](PRIVACY_TRE_EM.md) — cũng hiển thị ở khay hệ thống và trang “Hôm nay em đã dùng gì”.

## 1. Nguyên tắc
Đối chiếu sáu nguyên tắc thiết kế của đề bài: (NT1) biểu tượng khay luôn hiện, không có chế độ ẩn; (NT2) tối thiểu hóa dữ liệu; (NT3) trẻ có tiếng nói — xin thêm giờ, báo chặn nhầm; (NT4) mọi lần chặn đều được giải thích, nêu ai đặt quy tắc; (NT5) minh bạch hai chiều — trẻ xem cùng báo cáo và nhật ký đổi quy tắc; (NT6) danh sách an toàn vĩnh viễn (cổng trường, 111, khẩn cấp).

## 2. Dữ liệu được lưu — trường ↔ mục đích ↔ thời hạn ↔ người xem

### 2.1 Sự kiện sử dụng (bảng `events`, đúng lược đồ F3)
| Trường | Nội dung | Mục đích | Lưu tối đa | Ai xem được |
|---|---|---|---|---|
| `event_id` | mã ngẫu nhiên do agent sinh | chống ghi trùng khi gửi lại (idempotency) | 90 ngày | hệ thống |
| `ts` | thời điểm (UTC) | vẽ biểu đồ theo ngày/tuần, đối chiếu lịch | 90 ngày | phụ huynh, trẻ |
| `device_id` | mã thiết bị | phân biệt nhiều máy của một trẻ | đến khi gỡ thiết bị | phụ huynh, trẻ |
| `child_id` | mã hồ sơ trẻ | áp đúng chính sách theo độ tuổi | đến khi xóa hồ sơ | phụ huynh, trẻ |
| `type` | `app_start`, `app_stop`, `domain_query`, `blocked_app`, `blocked_domain`, `quota_warning`, `locked`, `unlock_request`, `override_granted` | phân loại hoạt động | 90 ngày | phụ huynh, trẻ |
| `subject` | tên tệp ứng dụng **hoặc** tên miền (không đường dẫn, không tham số) | báo cáo top ứng dụng/tên miền, giải thích lần chặn | 90 ngày | phụ huynh, trẻ |
| `duration_sec` | số giây | trừ dần hạn mức, biểu đồ | 90 ngày | phụ huynh, trẻ |
| `policy_id` | phiên bản quy tắc + lý do (vd `v3:category:games`) | giải thích “vì sao bị chặn” và “ai đặt” | 90 ngày | phụ huynh, trẻ |

Server **từ chối** (HTTP 200 kèm `rejected`) mọi sự kiện có `subject` giống URL/đường dẫn, và kiểm tra `type`, `ts` (không ở tương lai >5 phút, không cũ hơn 90 ngày).

### 2.2 Dữ liệu khác
| Dữ liệu | Mục đích | Lưu | Ai xem |
|---|---|---|---|
| Email, tên hiển thị, **băm mật khẩu Argon2id**, bí mật TOTP (mã hóa AES-256-GCM) | đăng nhập | đến khi xóa tài khoản | chủ tài khoản (không bao giờ hiển thị lại mật khẩu/TOTP) |
| Phiên đăng nhập (băm token, IP, hạn) | đăng nhập 12 giờ, đăng xuất phía server | đến khi hết hạn rồi bị dọn | hệ thống |
| Mức dùng theo ngày (`daily_usage`) | hạn mức, báo cáo | 90 ngày | phụ huynh, trẻ |
| Yêu cầu của trẻ (xin giờ/báo chặn nhầm) | trẻ có tiếng nói | 90 ngày sau khi xử lý | phụ huynh, trẻ |
| Mã ghép cặp (băm, hạn 10 phút) kèm **bản ghi đồng ý**: phiên bản văn bản đồng ý, thời điểm, IP, xác nhận đã thông báo cho trẻ | bằng chứng phụ huynh đồng ý lắp đặt | mã dọn sau 1 ngày; ghi nhận đồng ý nằm trong nhật ký kiểm toán | phụ huynh, trẻ (mục nhật ký) |
| **Nhật ký kiểm toán** (ai, lúc nào, IP, giá trị cũ → mới; có chuỗi băm chống sửa/xóa) | minh bạch hai chiều NT5 | giữ lâu dài — chỉ chứa thay đổi quy tắc/sự kiện quản trị, **không** chứa dữ liệu sử dụng | phụ huynh, trẻ (phần liên quan đến trẻ) |
| Bộ nhớ đệm trên máy (SQLite): chính sách đã ký, mức dùng hôm nay, hàng đợi sự kiện chưa gửi | chạy khi mất mạng | ≤ 90 ngày; xóa theo lệnh “xóa dữ liệu” hoặc khi gỡ cài đặt | trẻ thấy qua khay |
| Bí mật của thiết bị trên máy (refresh token, khóa ký) | xác thực với server | đến khi gỡ; bảo vệ bằng DPAPI (Windows, phạm vi máy) | tiến trình dịch vụ |

### 2.3 Trường bị cấm tuyệt đối
URL đầy đủ/tham số tìm kiếm, phím gõ, ảnh/video màn hình, nội dung tin nhắn/email/tài liệu/clipboard, mã theo dõi của bên thứ ba. Mã nguồn không có SDK phân tích hay quảng cáo; server không gọi dịch vụ ngoài nào. (Ngoại lệ kỹ thuật không phải “dữ liệu gửi đi”: agent chuyển tiếp truy vấn DNS tới máy chủ DNS thượng nguồn do phụ huynh cấu hình `OPENGUARD_UPSTREAM_DNS`, như mọi máy tính khi duyệt web.)

## 3. Quyền và cách thực hiện (có trong sản phẩm)
| Quyền | Cách thực hiện |
|---|---|
| Biết dữ liệu nào được thu thập | Trang “Hôm nay em đã dùng gì”, mục “OpenGuard ghi lại những gì?” ở khay, bảng ở mục 2 |
| Truy cập/sao chép | `GET /api/v1/children/{id}/export` (JSON) và `/events.csv` (nút trên Dashboard) |
| Xóa | **“Xóa toàn bộ dữ liệu của con tôi”**: `DELETE /api/v1/children/{id}/data` với xác nhận `XOA DU LIEU` → xóa `events`, `daily_usage`, yêu cầu trên server và gửi lệnh `purge_local_data` để agent xóa bộ nhớ đệm cục bộ |
| Rút lại đồng ý | Gỡ thiết bị (`DELETE /api/v1/devices/{id}`) hoặc `python main_service.py unenroll` (khôi phục DNS, xóa dữ liệu cục bộ); xóa hồ sơ trẻ xóa mọi dữ liệu liên quan |
| Hạn chế lưu trữ | Tự xóa quá 90 ngày (`retention.py`, chạy khi khởi động và mỗi 6 giờ) |
| Trẻ có tiếng nói | Nút “Xin thêm giờ”, “Báo chặn nhầm”; tài khoản chỉ-xem của trẻ |

Lưu ý trung thực: nhật ký kiểm toán được **giữ lại** sau khi xóa dữ liệu sử dụng, vì nó là bằng chứng minh bạch (ai đổi quy tắc, ai đồng ý cài đặt) và không chứa dữ liệu hoạt động của trẻ; xóa nó sẽ phá chuỗi băm. Nếu cần xóa cả nhật ký, chủ hệ thống phải xóa cơ sở dữ liệu.

## 4. Căn cứ pháp lý (tham chiếu — **nhóm cần đối chiếu lại với văn bản gốc trước khi nộp**)
Đề bài nêu Luật An ninh mạng 2018 và Nghị định 13/2023/NĐ-CP; các văn bản này đã được thay thế/sửa đổi. Tại thời điểm làm bài, các văn bản hiện hành được tham chiếu gồm (đã tra cứu trên nguồn công khai, cần xác nhận lại trên cổng văn bản chính thức như vbpl.vn / thuvienphapluat.vn):

| Văn bản | Điều khoản liên quan | Hiện thực trong hệ thống |
|---|---|---|
| **Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15** (hiệu lực 01/01/2026) | Điều 3 (nguyên tắc: lưu trữ phù hợp mục đích); Điều 9 (sự đồng ý); Điều 10 (rút lại đồng ý); Điều 14 (xóa, hủy dữ liệu); Điều 24 (dữ liệu cá nhân của trẻ em: người đại diện thực hiện quyền; trẻ từ đủ 7 tuổi cần có thêm sự đồng ý của trẻ trong một số trường hợp, ví dụ công bố/tiết lộ đời sống riêng tư) | Đồng ý của phụ huynh được ghi nhận khi tạo mã ghép cặp (có xác nhận “đã thông báo cho trẻ”); tối thiểu hóa; tự xóa 90 ngày; xóa theo yêu cầu; **không công bố/tiết lộ cho bên thứ ba** |
| **Nghị định 356/2025/NĐ-CP** (hiệu lực 01/01/2026; thay thế NĐ 13/2023/NĐ-CP) | hướng dẫn thi hành Luật BVDLCN | như trên |
| **Luật An ninh mạng số 116/2025/QH15** (hiệu lực 01/07/2026; thay Luật ANM 2018 và Luật An toàn thông tin mạng 2015) | Điều 16 (phòng, chống hành vi xâm hại trẻ em trên không gian mạng) | lọc tên miền theo 6 nhóm, SafeSearch, danh sách an toàn |
| **Luật Trẻ em 2016** | Điều 21 (quyền bí mật đời sống riêng tư) | không đọc nội dung, không ghi phím/màn hình; trẻ xem được mọi dữ liệu về mình |
| **Quyết định 830/QĐ-TTg ngày 01/6/2021** | chương trình bảo vệ và hỗ trợ trẻ em tương tác lành mạnh trên môi trường mạng, giai đoạn 2021–2025 | định hướng thiết kế “đồng hành, đối thoại” |

> Ghi chú: số điều khoản trên do trợ lý AI tra cứu và tóm tắt; việc trích dẫn trong báo cáo nộp cho giảng viên phải sao chép chính xác từ văn bản gốc (đề bài yêu cầu trích dẫn đúng điều khoản). Đây là tài liệu kỹ thuật, không phải tư vấn pháp lý.

## 4a. Quyết định về chế độ mất kết nối (F4)
Agent luôn thực thi bằng chính sách đã lưu (đã xác minh chữ ký). Gói có hạn **7 ngày**; nếu quá hạn mà vẫn mất kết nối, agent chuyển sang **chính sách an toàn mặc định** (hạn mức 120/180 phút, khung 06:00–21:00, nhóm mặc định cho trẻ 6–11; danh sách an toàn vĩnh viễn vẫn giữ) — không mở không giới hạn (tránh lách luật bằng cách ngắt mạng) và không khóa vô hạn (tránh trẻ mất đường liên lạc/học tập). Đây là lựa chọn “fail-safe default”, không phải fail-open hay fail-closed tuyệt đối.

## 5. Danh sách an toàn vĩnh viễn (NT6)
Mã nguồn cố định (`app/classification.py::SAFETY_WHITELIST`), không có API sửa: `edu.vn`, `gov.vn`, `tongdai111.vn`, `vnedu.vn`, `classroom.google.com`. Được kiểm thử rằng dù nhóm bị chặn hay phụ huynh chặn riêng, các tên miền này vẫn được phân giải; DNS proxy và chặn ứng dụng không áp dụng cho chúng. *(Danh sách miền cụ thể của trường/tổng đài cần được nhóm xác nhận với nguồn chính thức trước khi triển khai thật.)*

## 6. Giới hạn đã biết
- DNS proxy hiện xử lý UDP; trình duyệt dùng DoH tới nhà cung cấp lạ, VPN hoặc đổi DNS bằng quyền quản trị vẫn là hướng vượt qua (xem `THREATMODEL.md`, báo cáo mạng M3).
- Agent chạy trên máy của trẻ nên không chống được người có quyền Administrator; hệ thống chủ động **không** chống gỡ cài đặt (cấm theo đề bài) mà thay vào đó gửi cảnh báo khi agent ngừng liên lạc/bị gỡ.
