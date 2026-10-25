# OpenGuard Kids — Mô hình mối đe dọa (STRIDE) & danh mục kiểm tra OWASP ASVS

> Phạm vi: Agent Windows, Server FastAPI, Dashboard web. Mức tin cậy: **máy của trẻ là môi trường không tin cậy hoàn toàn** (trẻ có thể là kẻ tấn công), phụ huynh là chủ sở hữu hợp pháp.

## 1. Tài sản & ranh giới tin cậy
| Tài sản | Vì sao quan trọng |
|---|---|
| Hồ sơ/dữ liệu sử dụng của trẻ | dữ liệu cá nhân của trẻ em |
| Chính sách đã ký | nếu bị giả, trẻ tự gỡ giới hạn hoặc kẻ xấu khóa/chặn máy |
| Thông tin xác thực phụ huynh, khóa chủ `OGK_MASTER_KEY` | chiếm quyền toàn hệ thống |
| Token/khóa thiết bị | giả danh agent |

Ranh giới: (1) Trình duyệt phụ huynh ⇄ Server (TLS, cookie phiên + CSRF); (2) Agent ⇄ Server (TLS 1.2+, ghim chứng chỉ, token 15 phút + refresh xoay vòng, gói chính sách ký HMAC theo thiết bị); (3) Dịch vụ SYSTEM ⇄ giao diện khay (HTTP 127.0.0.1 + token + kiểm tra Host); (4) Máy của trẻ (người dùng ≠ quản trị).

## 2. Bảng STRIDE (14 mối đe dọa)
| # | Loại | Mối đe dọa | Biện pháp trong mã | Kiểm thử | Rủi ro còn lại |
|---|---|---|---|---|---|
| T1 | Spoofing | Kẻ giữa đường/máy chủ giả gửi chính sách nới lỏng cho agent | HMAC-SHA256 trên JSON chuẩn hóa, khóa **riêng từng thiết bị** (HKDF); ràng buộc `device_id`; từ chối phiên bản thấp hơn (chống phát lại); ghim chứng chỉ | `test_tampered_policy_bundle_is_rejected…`, `test_bundle_signature_and_device_binding` | Nếu lộ `OGK_MASTER_KEY` thì giả mạo được mọi thiết bị |
| T2 | Spoofing | Dò mã ghép cặp / tái sử dụng mã | Mã 8 ký tự (32 ký tự không nhầm lẫn ⇒ ~40 bit), hiệu lực 10 phút, **dùng một lần** (UPDATE có điều kiện), giới hạn tốc độ theo IP, băm khi lưu | `test_enrollment_code_single_use_expiry_and_consent` | Kẻ đứng sau NAT chung IP có thể dùng chung hạn mức tốc độ |
| T3 | Spoofing | Chiếm tài khoản phụ huynh (đoán mật khẩu) | Argon2id, ≥10 ký tự, khóa 15 phút sau 5 lần sai, giới hạn IP, thông báo lỗi chung, TOTP tùy chọn (chống dùng lại mã), đổi mật khẩu hủy các phiên khác | `test_login_lockout…`, `test_totp_login_flow`, `test_totp_replay_rejected` | Chưa có quên mật khẩu qua email (không triển khai) |
| T4 | Tampering | Sửa gói chính sách/DB cục bộ để xóa hạn mức | Gói đã ký; hạn mức `max()` chỉ tăng (cả server lẫn agent); đồng hồ tin cậy neo theo giờ server | `test_tampered…`, `test_clock_rollback_cannot_extend_the_day`, `test_offline_store…` | Người có quyền Administrator/SYSTEM vẫn sửa được bộ đếm cục bộ — chỉ phát hiện qua chênh lệch với server |
| T5 | Tampering | Chỉnh đồng hồ hệ thống lùi/tiến để kéo dài ngày hoặc reset hạn mức | `ClockGuard`: so lệch đồng hồ hệ thống với `monotonic`; quyết định dựa trên đồng hồ tin cậy; báo `clock_tamper_detected` lên nhật ký kiểm toán | `test_clock_guard_detects_rollback_and_ignores_it` | Sau khi ngủ/ngủ đông lâu, đồng hồ tin cậy có thể chậm cho tới lần heartbeat kế tiếp |
| T6 | Repudiation | “Con không xin thêm giờ”, “ba/mẹ không đổi quy tắc” | Nhật ký kiểm toán có chuỗi băm SHA-256 (ai/lúc nào/IP/cũ→mới); trẻ xem được | `test_audit_chain_detects_tampering`, `test_policy_update_versions_audit_log_and_commands` | Quản trị CSDL có thể thay toàn bộ chuỗi (không có neo ngoài) |
| T7 | Info. disclosure | Phụ huynh A đọc dữ liệu trẻ nhà B (IDOR) | Mọi truy vấn lọc theo chủ sở hữu ở mức SQL, trả 404; vai trò `child_view` chỉ đọc đúng một trẻ; `admin` không xem dữ liệu trẻ | `test_idor_other_parent_cannot_access…`, `test_child_view_is_read_only_and_scoped`, `test_security_headers_and_admin_cannot_read_child_data` | — |
| T8 | Info. disclosure | Lộ dữ liệu khi truyền/lưu | TLS 1.2+, HSTS (prod), cookie HttpOnly/Secure/SameSite=Lax, `Cache-Control: no-store`, bí mật TOTP mã hóa AES-GCM, refresh token chỉ lưu băm, bí mật agent bảo vệ DPAPI | `test_session_cookie_flags…`, `test_field_encryption_roundtrip_and_tamper` | Cơ sở dữ liệu SQLite chưa mã hóa toàn bộ (dựa vào quyền tệp/đĩa) |
| T9 | Info. disclosure | Trang web độc hại gọi API cục bộ của agent (DNS rebinding/CSRF cục bộ) | IPC chỉ 127.0.0.1, bắt buộc header `X-OG-Token`, kiểm tra `Host`, không có API đổi chính sách | (kiểm thử thủ công; mô tả ở `ipc.py`) | Tiến trình độc hại cùng người dùng đọc được `ipc.json` |
| T10 | DoS | Làm ngập heartbeat/sự kiện/đăng nhập | Giới hạn tốc độ (đăng nhập theo IP, chung theo IP), lô sự kiện ≤ 500, trường có độ dài tối đa, SQLite WAL + busy_timeout | `test_sliding_window_limiter` | Không có WAF/cân bằng tải; giới hạn đang lưu trong bộ nhớ một tiến trình |
| T11 | Elevation | CSRF hoặc tài khoản trẻ thực hiện thao tác phụ huynh | Token CSRF theo phiên (so sánh hằng thời gian), phân quyền theo vai trò ở từng route | `test_session_cookie_flags_csrf…`, `test_child_view_is_read_only…` | — |
| T12 | **Child as attacker** | Trẻ tìm cách thoát giới hạn | Xem bảng 3 | `test_dns_doh…`, `test_parse_netsh_and_repair_drift`, `test_app_block_by_name_and_by_hash_even_if_renamed` | Quản trị viên cục bộ, khởi động từ USB, máy thứ hai, mạng di động: **không chặn được** |
| T13 | **Stalkerware / lạm dụng** | Người lớn cài OpenGuard lên máy của người khác để theo dõi lén | Không có chế độ ẩn; biểu tượng khay luôn hiện + thông báo khi khởi động; dịch vụ có tên/mô tả rõ ràng; ghép cặp cần mã do tài khoản tạo kèm xác nhận “đã thông báo cho trẻ”; người dùng máy có thể `unenroll` bất cứ lúc nào không cần mật khẩu; lược dữ liệu tối thiểu (không phím/màn hình/nội dung); chỉ nhóm tuổi < 18 | `test_enrollment_code…`, `test_urgent…` | Người có quyền quản trị vẫn cài bằng dòng lệnh mà không ai thấy cho tới khi khay hiện; nên có cảnh báo cộng đồng/liên hệ hỗ trợ nạn nhân (xem §4) |
| T14 | Tampering | Chuỗi cung ứng/phụ thuộc có lỗ hổng | Phiên bản phụ thuộc được ghim; không dùng SDK bên thứ ba | — | **Chưa chạy** `pip-audit`/`npm audit` |

## 3. Chi tiết T12 — trẻ là kẻ tấn công
| Kỹ thuật vượt qua | Đối phó đã làm | Còn thiếu / giới hạn |
|---|---|---|
| Đổi DNS sang 8.8.8.8 | `DnsGuard.check_and_repair()` mỗi 30 giây đặt lại 127.0.0.1 | Cần quyền Administrator để đặt DNS; trẻ có quyền này thì đổi lại được |
| DNS-over-HTTPS trong trình duyệt | NXDOMAIN cho nhà cung cấp DoH phổ biến + canary `use-application-dns.net` | DoH tới nhà cung cấp chưa có trong danh sách |
| VPN/Proxy/Tor | (mức DNS) chặn tên miền dịch vụ thuộc nhóm “không phù hợp”; thời gian vẫn đếm theo hoạt động máy | VPN client không bị phát hiện ở mức gói tin |
| Hosts file / IP trực tiếp | — | Truy cập bằng IP không qua DNS **không bị lọc**; chỉ chặn được qua tường lửa (chưa làm) |
| Tự chạy `unenroll`/gỡ dịch vụ | Cho phép (đề bài cấm chống gỡ) nhưng agent gửi `uninstall-notice`: server ghi nhật ký `agent_uninstalled`, phụ huynh và trẻ thấy trong nhật ký; thư mục dữ liệu chỉ SYSTEM/Administrators ghi được (do trình cài đặt đặt ACL) | Nếu trẻ là Administrator thì gỡ được — đó là hành vi chủ ý |
| Kill/đổi tên tiến trình, đổi tên `.exe` | Chặn theo tên **hoặc** SHA-256; dịch vụ SYSTEM, trẻ không có quyền dừng; heartbeat vắng mặt hiển thị “Ngoại tuyến” | Chưa có thông báo đẩy khi agent im lặng quá lâu |
| Lùi/tiến đồng hồ | ClockGuard (T5) | — |
| Đăng nhập tài khoản Windows khác / Chế độ an toàn / USB | — | Ngoài phạm vi phần mềm; cần BitLocker/BIOS/tài khoản chuẩn (không quản trị) cho trẻ |
| Cắt mạng để không nhận chính sách | Vẫn thực thi chính sách đã lưu; hết hạn 7 ngày → chính sách an toàn mặc định | — |
| Máy thứ hai/điện thoại | — | Chỉ quản lý các thiết bị đã cài |

Khuyến nghị triển khai: tạo tài khoản Windows **chuẩn (không phải Administrator)** cho trẻ.

## 4. T13 — Kịch bản stalkerware và các nguyên tắc đối kháng lạm dụng
Dự án bám các nguyên tắc cơ bản của Liên minh chống stalkerware: (1) **không ẩn**: không có tuỳ chọn ẩn biểu tượng/tiến trình; (2) **đồng ý có thể kiểm chứng**: mã ghép cặp tạo ra bởi tài khoản phụ huynh có xác nhận; (3) **minh bạch với người bị giám sát**: người dùng máy xem được mọi thứ được ghi và nhật ký thay đổi; (4) **dễ gỡ**: `unenroll` và gỡ dịch vụ không cần mật khẩu; (5) **dữ liệu tối thiểu**: không vị trí, không nội dung, không ảnh. Nếu nhóm nhận thấy kịch bản lạm dụng, cần bổ sung hướng dẫn liên hệ hỗ trợ nạn nhân và cho phép chủ máy xem “ai đã ghép cặp máy này”.

## 5. Danh mục kiểm tra OWASP ASVS (v4.0.3, mức L1 chọn lọc — 26 mục)
Trạng thái: ✅ đã làm & có kiểm thử/bằng chứng · 🟡 làm một phần · ❌ chưa làm.

| ASVS | Yêu cầu | TT | Ghi chú/bằng chứng |
|---|---|---|---|
| 2.1.1 | Độ dài mật khẩu tối thiểu | 🟡 | 10 ký tự theo đề bài (ASVS khuyến nghị 12) |
| 2.1.2 | Cho phép ≥64 và tối đa ≤128 ký tự | 🟡 | tối đa 256 ký tự |
| 2.1.7 | Kiểm tra mật khẩu lộ lọt | ❌ | chưa tích hợp danh sách mật khẩu bị lộ |
| 2.2.1 | Chống tự động hóa/brute force | ✅ | khóa 15 phút/5 lần + giới hạn IP; `test_login_lockout…` |
| 2.4.1 | Băm mật khẩu bằng thuật toán chuẩn (Argon2id) | ✅ | `security.py` |
| 2.5.x | Khôi phục thông tin xác thực | ❌ | không có quên mật khẩu qua email |
| 2.8.x | OTP một lần/TOTP | ✅ | RFC 6238, chống dùng lại; `test_totp_rfc6238_vector` |
| 3.2.1 | Token phiên mới mỗi lần đăng nhập | ✅ | `secrets.token_urlsafe` |
| 3.3.1 | Đăng xuất vô hiệu hóa phiên phía server | ✅ | `test_session_cookie_flags_csrf_and_server_side_logout` |
| 3.3.2 | Hết hạn phiên | ✅ | 12 giờ tuyệt đối |
| 3.4.1–3.4.3 | Cookie Secure/HttpOnly/SameSite | ✅ | Secure bật khi `ENV=prod`/`COOKIE_SECURE` |
| 4.1.3 | Nguyên tắc đặc quyền tối thiểu theo vai trò | ✅ | parent / child_view / admin |
| 4.2.1 | Chống IDOR | ✅ | 404 ở mức truy vấn; `test_idor_…` |
| 4.2.2 | CSRF cho thao tác thay đổi trạng thái | ✅ | token theo phiên |
| 5.1.3 | Kiểm tra đầu vào theo whitelist | ✅ | pydantic + regex tên miền/ứng dụng/sự kiện |
| 5.3.4 | Truy vấn tham số hóa (chống SQLi) | ✅ | SQLAlchemy ORM |
| 5.3.x | Mã hóa đầu ra (XSS) | ✅ | React escape; CSP `default-src 'self'` |
| 6.2.x | Thuật toán mật mã chuẩn | ✅ | AES-256-GCM, HMAC-SHA256, HKDF |
| 6.4.x | Quản lý khóa | 🟡 | khóa dẫn xuất từ khóa chủ; **chưa** có luân chuyển khóa |
| 7.1.x | Không ghi dữ liệu nhạy cảm vào log | 🟡 | không log mật khẩu/token; chưa có rà soát tự động |
| 8.1.x | Bảo vệ dữ liệu nhạy cảm/ tối thiểu hóa | ✅ | lược đồ sự kiện giới hạn; `no-store` |
| 9.1.x | TLS cho mọi kết nối | 🟡 | hỗ trợ TLS + ghim; triển khai thật cần chứng chỉ hợp lệ |
| 11.1.x | Giới hạn logic nghiệp vụ | ✅ | mã dùng một lần, lô sự kiện ≤500, thưởng giờ ≤240 phút |
| 13.2.x | API REST kiểm tra schema/ loại nội dung | ✅ | FastAPI/pydantic |
| 14.2.x | Quản lý phụ thuộc | 🟡 | ghim phiên bản; chưa chạy công cụ quét lỗ hổng |
| 14.4.x | Header an toàn | ✅ | `X-Content-Type-Options`, `X-Frame-Options`, CSP, `Referrer-Policy`, HSTS |
| 14.5.x | CORS hạn chế | ✅ | danh sách origin cấu hình, chỉ method cần thiết |
