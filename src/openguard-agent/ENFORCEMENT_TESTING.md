# Thử nghiệm thực thi (enforcement)

Mặc định agent ở **dry-run**: tính quyết định và ghi log `[ENFORCEMENT] DRY_RUN`, không khóa máy, không tắt ứng dụng, không đổi DNS.

## Bật từng phần (chỉ trên máy/tài khoản thử nghiệm của nhóm)
1. Ghép cặp agent với server, đặt hạn mức 1–2 phút trong dashboard.
2. `setx OPENGUARD_ENFORCE_LOCK 1 /M` rồi khởi động lại dịch vụ → hết giờ: cảnh báo 10/5/1 phút + 60 giây ân hạn rồi khóa phiên. Lịch ngoài giờ/khóa ngay: khóa tức thì.
3. `OPENGUARD_ENFORCE_APPS=1`: thử với ứng dụng vô hại (Notepad) đặt vào danh sách chặn; agent tắt và ghi sự kiện `app_blocked`.
4. `OPENGUARD_MANAGE_DNS=1` (quyền quản trị): bật proxy DNS cổng 53, đặt DNS adapter về 127.0.0.1; `DnsGuard` sửa lại nếu bị đổi. Hoàn tác: `main_service.py unenroll` khôi phục DNS cũ; nếu cần, đặt DNS tự động trong Cài đặt mạng.
5. Danh sách an toàn (edu.vn, gov.vn, 111…) không bao giờ bị chặn; lệnh khóa không khóa các đường gọi khẩn cấp.

## Gỡ
`main_service.py service stop` → `service remove` → `unenroll`. Gỡ cài đặt sẽ gửi thông báo `agent_uninstalled` cho phụ huynh (không chống gỡ).
