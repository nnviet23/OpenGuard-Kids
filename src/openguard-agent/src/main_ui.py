"""Giao diện khay hệ thống (phiên người dùng) – biểu tượng LUÔN hiển thị (NT1), không có chế độ ẩn.

Hiển thị: thời gian còn lại, thông báo (cảnh báo 10/5/1 phút, lý do bị chặn + ai đặt quy tắc),
màn hình “Hôm nay em đã dùng gì”, nhật ký thay đổi quy tắc, nút “Xin thêm giờ” và “Báo chặn nhầm”.
Giao diện chỉ đọc/gửi yêu cầu qua IPC cục bộ; không thể đổi chính sách.
"""
from __future__ import annotations

import html
import json
import os
import sys
import urllib.request
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (QApplication, QDialog, QInputDialog, QMenu, QMessageBox, QPushButton, QSystemTrayIcon,
                             QTextBrowser, QVBoxLayout)

ACTION_VI = {"policy_updated": "Đổi quy tắc", "override_granted": "Cho thêm giờ", "lock_now": "Khóa máy ngay",
             "unlock_now": "Mở khóa", "request_decided": "Trả lời yêu cầu", "device_enrolled": "Cài OpenGuard trên máy",
             "enroll_code_created": "Tạo mã cài đặt", "data_erased": "Xóa dữ liệu", "child_created": "Tạo hồ sơ",
             "device_revoked": "Gỡ máy"}


class Ipc:
    def __init__(self) -> None:
        data = os.getenv("OPENGUARD_DATA_DIR", os.path.join(os.getenv("PROGRAMDATA", str(Path.home() / ".openguard")), "OpenGuardKids"))
        cfg = json.loads((Path(data) / "ipc.json").read_text())
        self.base, self.token = f"http://127.0.0.1:{cfg['port']}", cfg["token"]

    def call(self, path: str, body: dict | None = None):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"X-OG-Token": self.token, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())


def make_icon(color: str) -> QIcon:
    pm = QPixmap(64, 64)
    pm.fill(QColor("transparent"))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(QColor("white"))
    p.drawEllipse(4, 4, 56, 56)
    p.setPen(QColor("white"))
    p.setFont(p.font())
    p.drawText(pm.rect(), 0x84, "OG")
    p.end()
    return QIcon(pm)


def fmt_remaining(sec: int | None) -> str:
    if sec is None:
        return "không giới hạn hôm nay"
    m = max(0, sec) // 60
    return f"{m // 60} giờ {m % 60} phút" if m >= 60 else f"{m} phút"


class Tray:
    def __init__(self, app: QApplication) -> None:
        self.app, self.ipc, self.last_id, self.status = app, Ipc(), 0, {}
        self.tray = QSystemTrayIcon(make_icon("#054b85"), app)
        menu = QMenu()
        self.title_action = QAction("OpenGuard Kids", menu)
        self.title_action.setEnabled(False)
        menu.addAction(self.title_action)
        menu.addSeparator()
        for label, fn in (("Hôm nay em đã dùng gì?", self.show_today), ("Xin thêm giờ…", self.ask_time),
                          ("Con nghĩ trang này bị chặn nhầm…", self.report_block),
                          ("Nhật ký thay đổi quy tắc", self.show_rules), ("OpenGuard ghi lại những gì?", self.show_privacy),
                          ("Yêu cầu của con", self.show_requests)):
            a = QAction(label, menu)
            a.triggered.connect(fn)
            menu.addAction(a)
        menu.addSeparator()
        quit_a = QAction("Đóng cửa sổ này (dịch vụ vẫn chạy)", menu)
        quit_a.triggered.connect(app.quit)
        menu.addAction(quit_a)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip("OpenGuard Kids đang hoạt động")
        self.tray.show()  # luôn hiện – không có tùy chọn ẩn
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll)
        self.timer.start(2000)
        self.poll()

    def poll(self) -> None:
        try:
            st = self.ipc.call(f"/status?since={self.last_id}")
        except Exception:
            self.tray.setIcon(make_icon("#888888"))
            self.tray.setToolTip("OpenGuard Kids: chưa kết nối được dịch vụ")
            return
        self.status = st
        for n in st.get("notifications", []):
            self.last_id = max(self.last_id, n["id"])
            icon = QSystemTrayIcon.MessageIcon.Warning if n["kind"] in ("warn", "block", "lock") else QSystemTrayIcon.MessageIcon.Information
            self.tray.showMessage(n["title"], n["body"], icon, 10000)
        rem = st.get("remaining_seconds")
        line = f"Còn lại hôm nay: {fmt_remaining(rem)}" if st.get("status") == "ALLOWED" else {
            "QUOTA_EXCEEDED": "Đã hết thời gian hôm nay", "OUTSIDE_ALLOWED_SCHEDULE": "Ngoài khung giờ được phép",
            "FORCED_LOCK": "Phụ huynh đã khóa máy"}.get(st.get("status"), "Đang hoạt động")
        extra = "" if st.get("online") else " • đang offline (dùng quy tắc đã lưu)"
        if not st.get("enforce_lock"):
            extra += " • chế độ thử (chưa khóa thật)"
        self.title_action.setText(line + extra)
        self.tray.setToolTip("OpenGuard Kids – " + line)
        color = "#2e7d32" if st.get("status") == "ALLOWED" else "#c62828"
        self.tray.setIcon(make_icon(color if st.get("online") else "#ef6c00"))
        if st.get("should_lock") and sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.LockWorkStation()  # trong phiên người dùng nên có hiệu lực

    # ---- dialogs ----
    def _page(self, title: str, body_html: str) -> None:
        d = QDialog()
        d.setWindowTitle(title)
        d.resize(560, 520)
        lay = QVBoxLayout(d)
        tb = QTextBrowser()
        tb.setHtml(body_html)
        lay.addWidget(tb)
        b = QPushButton("Đóng")
        b.clicked.connect(d.accept)
        lay.addWidget(b)
        d.exec()

    def _fetch(self, path: str):
        try:
            return self.ipc.call(path)
        except Exception as e:
            QMessageBox.warning(None, "OpenGuard", f"Chưa lấy được dữ liệu từ máy chủ: {e}")
            return None

    def show_today(self) -> None:
        d = self._fetch("/transparency")
        if not d:
            return
        t = d["today"]
        apps = "".join(f"<li>{html.escape(a['name'])} – {a['minutes']} phút</li>" for a in t["apps"]) or "<li>Chưa có</li>"
        sites = "".join(f"<li>{html.escape(s['domain'])} ({s['count']} lần)</li>" for s in t["sites"]) or "<li>Chưa có</li>"
        blocks = "".join(f"<li><b>{html.escape(b['subject'])}</b>: {html.escape(b['why'])}. Quy tắc do <b>{html.escape(b['rule_set_by'])}</b> đặt.</li>" for b in t["blocks"]) or "<li>Hôm nay chưa có gì bị chặn</li>"
        no = "".join(f"<li>{html.escape(x)}</li>" for x in t["not_collected"])
        self._page("Hôm nay em đã dùng gì?", f"<h2>Xin chào {html.escape(t['child_name'])}!</h2>"
                   f"<p>Hôm nay con đã dùng <b>{t['used_minutes']} phút</b> / {t['limit_minutes']} phút (còn {t['remaining_minutes']} phút).</p>"
                   f"<h3>Ứng dụng</h3><ul>{apps}</ul><h3>Trang web (chỉ tên miền)</h3><ul>{sites}</ul><h3>Những lần bị chặn</h3><ul>{blocks}</ul>"
                   f"<h3>OpenGuard KHÔNG ghi lại</h3><ul>{no}</ul><p>Ba/mẹ cũng thấy đúng những thông tin này.</p>")

    def show_rules(self) -> None:
        d = self._fetch("/transparency")
        if not d:
            return
        rows = "".join(f"<tr><td>{r['ts'][:16].replace('T', ' ')}</td><td>{html.escape(r['actor'])}</td><td>{ACTION_VI.get(r['action'], r['action'])}</td></tr>" for r in d["rule_log"]) or "<tr><td>Chưa có thay đổi</td></tr>"
        self._page("Nhật ký thay đổi quy tắc", f"<p>Ai đã đổi gì và khi nào – con xem được tất cả.</p><table cellpadding=4>{rows}</table>")

    def show_privacy(self) -> None:
        self._page("OpenGuard ghi lại những gì?", "<h3>Có ghi</h3><ul><li>Tên ứng dụng con mở và thời gian dùng</li><li>Tên miền trang web (không phải địa chỉ đầy đủ)</li><li>Những lần bị chặn / xin thêm giờ</li></ul>"
                   "<h3>Không ghi</h3><ul><li>Tin nhắn, email, nội dung tài liệu</li><li>Tiêu đề cửa sổ, phím gõ, ảnh màn hình</li></ul>"
                   "<p>Dữ liệu tự xóa sau 90 ngày. Ba/mẹ có thể xóa toàn bộ bất cứ lúc nào. Trang của trường và tổng đài 111 không bao giờ bị chặn.</p>")

    def show_requests(self) -> None:
        rs = self._fetch("/requests")
        if rs is None:
            return
        rows = "".join(f"<li>{'Xin thêm ' + str(r['minutes']) + ' phút' if r['kind'] == 'more_time' else 'Báo chặn nhầm ' + html.escape(r['subject'])} – <b>{ {'pending': 'đang chờ', 'approved': 'ba/mẹ đồng ý', 'denied': 'ba/mẹ chưa đồng ý'}[r['status']] }</b> {html.escape(r['response_note'])}</li>" for r in rs) or "<li>Chưa có yêu cầu</li>"
        self._page("Yêu cầu của con", f"<ul>{rows}</ul>")

    def ask_time(self) -> None:
        m, ok = QInputDialog.getInt(None, "Xin thêm giờ", "Con muốn xin thêm bao nhiêu phút?", 15, 5, 120, 5)
        if not ok:
            return
        msg, ok = QInputDialog.getText(None, "Xin thêm giờ", "Con muốn nói gì với ba/mẹ? (không bắt buộc)")
        if ok:
            self._send({"kind": "more_time", "minutes": m, "message": msg})

    def report_block(self) -> None:
        dom, ok = QInputDialog.getText(None, "Báo chặn nhầm", "Tên trang web (ví dụ: example.com):")
        if ok and dom.strip():
            msg, _ = QInputDialog.getText(None, "Báo chặn nhầm", "Vì sao con cần trang này? (không bắt buộc)")
            self._send({"kind": "unblock", "subject": dom.strip(), "message": msg})

    def _send(self, body: dict) -> None:
        try:
            self.ipc.call("/request", body)
            QMessageBox.information(None, "Đã gửi", "Yêu cầu đã gửi cho ba/mẹ. Con sẽ nhận được trả lời ở đây.")
        except Exception as e:
            QMessageBox.warning(None, "Chưa gửi được", f"Không gửi được yêu cầu: {e}")


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("Không có khay hệ thống")
    tray = Tray(app)  # noqa: F841
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
