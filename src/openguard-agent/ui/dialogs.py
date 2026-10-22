from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QMessageBox, 
    QListWidget, QListWidgetItem
)


COMMON_STYLE = """
    QDialog {
        background-color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QLabel {
        color: #0f172a;
    }
    QLineEdit, QTextEdit {
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        background-color: #f8fafc;
        padding: 8px;
        font-size: 12px;
        color: #0f172a;
    }
    QLineEdit:focus, QTextEdit:focus {
        border-color: #0e8368;
        background-color: #ffffff;
    }
    QPushButton {
        padding: 7px 14px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
    }
    QPushButton#primaryBtn {
        background-color: #0e8368;
        color: #ffffff;
        border: none;
    }
    QPushButton#primaryBtn:hover {
        background-color: #09614c;
    }
    QPushButton#cancelBtn {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #475569;
    }
    QPushButton#cancelBtn:hover {
        background-color: #e2e8f0;
    }
"""
class RequestTimeDialog(QDialog):
    """Hộp thoại xin thêm 15 phút sử dụng (cố định)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Xin thêm 15 phút")
        self.setFixedSize(340, 250)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)
        self.setStyleSheet(COMMON_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("Xin thêm 15 phút sử dụng")
        title.setStyleSheet("font-size: 13px; font-weight: 700;")
        layout.addWidget(title)

        sub_desc = QLabel("Lý do em cần dùng thêm máy tính (gửi đến phụ huynh):")
        sub_desc.setStyleSheet("font-size: 11px; color: #475569;")
        layout.addWidget(sub_desc)

        self.reason_txt = QTextEdit()
        self.reason_txt.setPlaceholderText("Ví dụ: Em cần hoàn thành bài tập nộp trên lớp...")
        layout.addWidget(self.reason_txt)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)

        send_btn = QPushButton("Gửi yêu cầu")
        send_btn.setObjectName("primaryBtn")
        send_btn.clicked.connect(self._handle_send)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(send_btn)
        layout.addLayout(btn_layout)

    def _handle_send(self):
        reason = self.reason_txt.toPlainText().strip()
        if not reason:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập lý do sử dụng.")
            return

        QMessageBox.information(
            self, "Đã gửi", 
            f"Đã gửi yêu cầu thêm 15 phút tới phụ huynh với lý do:\n\"{reason}\""
        )
        self.accept()


class ReportBlockedDialog(QDialog):
    """Hộp thoại báo cáo trang web bị giới hạn nhầm"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Báo cáo trang web")
        self.setFixedSize(340, 210)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)
        self.setStyleSheet(COMMON_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("Báo cáo địa chỉ cần mở")
        title.setStyleSheet("font-size: 13px; font-weight: 700;")
        layout.addWidget(title)

        desc = QLabel("Nhập tên miền hoặc trang web học tập cần xem xét:")
        desc.setStyleSheet("font-size: 11px; color: #475569;")
        layout.addWidget(desc)

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("scratch.mit.edu, khanacademy.org...")
        layout.addWidget(self.domain_input)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Đóng")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)

        send_btn = QPushButton("Gửi báo cáo")
        send_btn.setObjectName("primaryBtn")
        send_btn.clicked.connect(self._handle_send)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(send_btn)
        layout.addLayout(btn_layout)

    def _handle_send(self):
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Thông báo", "Vui lòng điền tên miền trang web.")
            return

        QMessageBox.information(
            self, "Đã ghi nhận", 
            f"Đã chuyển yêu cầu mở trang '{domain}' đến phụ huynh."
        )
        self.accept()


class BlockedListDialog(QDialog):
    """Hộp thoại danh sách giới hạn - Chỉ đọc, không viền focus, scrollbar tự động"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Danh sách giới hạn")
        self.setFixedSize(320, 260)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)
        self.setStyleSheet(COMMON_STYLE + """
            QListWidget {
                outline: none;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                background-color: #f8fafc;
                font-family: Consolas, monospace;
                font-size: 12px;
                color: #334155;
            }
            QListWidget::item {
                padding: 7px 10px;
                border-bottom: 1px solid #f1f5f9;
            }
            /* Tắt hiệu ứng đổi màu / viền khi bấm chọn dòng */
            QListWidget::item:selected, 
            QListWidget::item:focus {
                background: transparent;
                color: #334155;
                border: none;
                outline: none;
            }
            /* Thanh cuộn hiện đại, chỉ hiện khi danh sách dài */
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("Mục đang được giới hạn hôm nay")
        title.setStyleSheet("font-size: 12px; font-weight: 700;")
        layout.addWidget(title)

        list_widget = QListWidget()
        
        # Tắt hoàn toàn việc focus và chọn phần tử để không bao giờ bị ô viền đen
        list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Thanh cuộn dọc chỉ hiện khi danh sách vượt quá chiều cao khung
        list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        items = [
            "roblox.com",
            "discord.com",
            "RobloxPlayer.exe"
        ]
        for it in items:
            list_widget.addItem(QListWidgetItem(it))

        layout.addWidget(list_widget)

        close_btn = QPushButton("Đóng")
        close_btn.setObjectName("cancelBtn")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
class PairingDialog(QDialog):
    """Hộp thoại kích hoạt máy trẻ bằng mã PIN 6 số từ phụ huynh"""
    def __init__(self, on_submit_callback, parent=None):
        super().__init__(parent)
        self.on_submit_callback = on_submit_callback
        self.setWindowTitle("Kích hoạt OpenGuard Kids")
        self.setFixedSize(320, 230)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)
        self.setStyleSheet(COMMON_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Kết nối với máy Phụ huynh")
        title.setStyleSheet("font-size: 13px; font-weight: 700;")
        layout.addWidget(title)

        desc = QLabel("Nhập mã PIN 6 số hiển thị trên Dashboard của ba mẹ để kích hoạt máy tính:")
        desc.setStyleSheet("font-size: 11px; color: #475569; line-height: 1.4;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Ô nhập mã PIN 6 số to, rõ ràng
        self.pin_input = QLineEdit()
        self.pin_input.setMaxLength(6)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setStyleSheet("""
            font-family: Consolas, monospace;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 6px;
            padding: 6px;
            color: #0e8368;
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
        """)
        self.pin_input.setPlaceholderText("000000")
        self.pin_input.returnPressed.connect(self._submit)
        layout.addWidget(self.pin_input)

        layout.addStretch()

        self.submit_btn = QPushButton("Kích hoạt ngay")
        self.submit_btn.setObjectName("primaryBtn")
        self.submit_btn.clicked.connect(self._submit)
        layout.addWidget(self.submit_btn)

    def _submit(self):
        pin = self.pin_input.text().strip()
        if len(pin) != 6 or not pin.isdigit():
            QMessageBox.warning(self, "Thông báo", "Mã PIN phải gồm đúng 6 chữ số.")
            return

        success, err_msg = self.on_submit_callback(pin)
        if success:
            QMessageBox.information(self, "Thành công", "Thiết bị đã kết nối thành công với tài khoản phụ huynh!")
            self.accept()
        else:
            QMessageBox.critical(self, "Kích hoạt thất bại", err_msg)