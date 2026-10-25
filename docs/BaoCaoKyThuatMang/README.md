# Báo cáo kỹ thuật mạng (M1–M6) – dàn bài và việc phải làm

Xuất file `BaoCaoKyThuatMang.pdf` từ tài liệu này sau khi **điền số liệu thật**. Không bịa số liệu.

| Mục | Nội dung | Nhóm phải làm trên máy Windows thật |
|---|---|---|
| M1 Luồng gói tin | Sơ đồ: trình duyệt → DNS proxy 127.0.0.1:53 → upstream; agent ↔ server (HTTPS, WS). Giải thích UDP/TCP 53, CNAME SafeSearch | Bắt Wireshark: truy vấn tên miền bị chặn (NXDOMAIN), cho phép, SafeSearch; chụp màn hình + lưu `.pcapng` |
| M2 So sánh cách chặn | DNS proxy vs hosts vs firewall IP vs proxy HTTP vs tắt tiến trình: ưu/nhược, độ chính xác, dễ bị vượt | Bảng so sánh có dẫn chứng thử nghiệm |
| M3 ≥7 cách vượt rào | DoH trong trình duyệt, đổi DNS thủ công, VPN, IP trực tiếp, hosts, proxy trình duyệt, đổi giờ máy, đổi tên file .exe, tài khoản khác… | Với mỗi cách: thử, ghi chặn được/không, biện pháp đối phó (DoH canary, DnsGuard, ClockGuard, hash SHA-256) và hạn chế còn lại |
| M4 Hiệu năng ≥30 mẫu | Độ trễ DNS có/không proxy; lan truyền chính sách; lệnh khóa | `python tools/measure_dns_latency.py --n 40`; `python tools/measure_propagation.py ...`; báo min/mean/median/p95 |
| M5 Chịu lỗi | Mất mạng, server sập, DB lỗi, upstream DNS lỗi → hành vi fail-safe | Ngắt mạng/tắt server khi agent chạy; ghi quan sát |
| M6 Đồng bộ thời gian | ClockGuard, neo giờ server, phát hiện đổi giờ; NTP | Đổi giờ máy ±1 giờ và ±1 ngày, ghi kết quả + sự kiện `clock_tamper_detected` |

## Số liệu sơ bộ từ máy giả lập Linux (không thay thế đo thật)
Trên server local, 30 lượt: lan truyền chính sách (đến khi heartbeat thấy phiên bản mới) ~14 ms; lệnh khóa qua WebSocket ~7 ms. Thực tế agent poll heartbeat mỗi 60 s nên trần cập nhật chính sách ≈ 60 s; lệnh khẩn qua WS ≤ 5 s khi kết nối còn.
