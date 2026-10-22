from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QFrame, QMessageBox
)
from ui.dialogs import RequestTimeDialog, ReportBlockedDialog, BlockedListDialog


class ActivitySummaryWindow(QWidget):
    def __init__(self, parent_tray=None):
        super().__init__()
        self.parent_tray = parent_tray

        # Thời gian (tính bằng giây)
        self.used_seconds = 1 * 3600 + 45 * 60  # 1h 45m
        self.total_quota_seconds = 2 * 3600     # 2h 00m
        self.remaining_seconds = max(0, self.total_quota_seconds - self.used_seconds)

        self._init_ui()
        self._setup_timer()

    def _init_ui(self):
        self.setWindowTitle("OpenGuard Kids")
        self.setFixedSize(340, 470)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #0f172a;
            }
            QProgressBar {
                border: 1px solid #e2e8f0;
                border-radius: 3px;
                text-align: right;
                height: 8px;
                background-color: #f1f5f9;
            }
            QProgressBar::chunk {
                background-color: #0e8368;
                border-radius: 2px;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton#actionBtn {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: 600;
                color: #334155;
            }
            QPushButton#actionBtn:hover {
                background-color: #f1f5f9;
                border-color: #94a3b8;
            }
            QPushButton#primaryActionBtn {
                background-color: #0e8368;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: 600;
                color: #ffffff;
            }
            QPushButton#primaryActionBtn:hover {
                background-color: #09614c;
            }
            QPushButton#linkBtn {
                background: none;
                border: none;
                color: #475569;
                font-size: 11px;
                text-decoration: underline;
                padding: 0;
                cursor: pointer;
            }
            QPushButton#linkBtn:hover {
                color: #0e8368;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        main_title = QLabel("Thời lượng sử dụng máy tính")
        main_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        sub_title = QLabel("Nguyên tắc minh bạch hai chiều (NT5)")
        sub_title.setStyleSheet("font-size: 11px; color: #64748b;")
        
        title_box.addWidget(main_title)
        title_box.addWidget(sub_title)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # Đường kẻ phân cách
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #f1f5f9; margin: 2px 0;")
        layout.addWidget(sep1)

        # 2. Khối đồng hồ đếm lùi
        countdown_panel = QVBoxLayout()
        countdown_panel.setSpacing(4)

        lbl_caption = QLabel("THỜI GIAN CÒN LẠI")
        lbl_caption.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        
        self.countdown_val = QLabel("15:00")
        self.countdown_val.setStyleSheet("font-family: Consolas, monospace; font-size: 32px; font-weight: 700; color: #0e8368;")

        countdown_panel.addWidget(lbl_caption)
        countdown_panel.addWidget(self.countdown_val)
        layout.addLayout(countdown_panel)

        # Thanh tiến trình
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.quota_desc = QLabel()
        self.quota_desc.setStyleSheet("font-size: 11px; color: #475569;")
        layout.addWidget(self.quota_desc)

        # Đường kẻ phân cách
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #f1f5f9; margin: 2px 0;")
        layout.addWidget(sep2)

        # 3. Phân loại 5 danh mục thuần chữ
        cat_header = QLabel("PHÂN BỔ THEO DANH MỤC")
        cat_header.setStyleSheet("font-size: 10px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;")
        layout.addWidget(cat_header)

        cats_layout = QVBoxLayout()
        cats_layout.setSpacing(6)
        cats_layout.addLayout(self._create_cat_row("Giáo dục", "1h 25m"))
        cats_layout.addLayout(self._create_cat_row("Giải trí", "20m"))
        cats_layout.addLayout(self._create_cat_row("Trò chơi", "0m"))
        cats_layout.addLayout(self._create_cat_row("Cổng thông tin điện tử", "0m"))
        cats_layout.addLayout(self._create_cat_row("Mạng xã hội", "0m"))
        layout.addLayout(cats_layout)

        # 4. Dòng liên kết xem danh sách đã hạn chế
        restrict_box = QHBoxLayout()
        self.btn_show_restricted = QPushButton("Danh sách đang hạn chế: 3 mục")
        self.btn_show_restricted.setObjectName("linkBtn")
        self.btn_show_restricted.clicked.connect(self._open_blocked_dialog)
        restrict_box.addWidget(self.btn_show_restricted)
        restrict_box.addStretch()
        layout.addLayout(restrict_box)

        layout.addStretch()

        # 5. Hai nút hành động ở chân trang
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        req_btn = QPushButton("Xin thêm giờ")
        req_btn.setObjectName("primaryActionBtn")
        req_btn.clicked.connect(self._open_request_dialog)

        rep_btn = QPushButton("Báo nhầm trang")
        rep_btn.setObjectName("actionBtn")
        rep_btn.clicked.connect(self._open_report_dialog)

        actions_layout.addWidget(req_btn, 1)
        actions_layout.addWidget(rep_btn, 1)
        layout.addLayout(actions_layout)

        self._update_display()

    def _create_cat_row(self, name: str, duration: str) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 12px; color: #334155;")
        
        lbl_time = QLabel(duration)
        lbl_time.setStyleSheet("font-family: Consolas, monospace; font-size: 12px; font-weight: 600; color: #0f172a;")
        
        row.addWidget(lbl_name)
        row.addStretch()
        row.addWidget(lbl_time)
        return row

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(1000)

    def _on_tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.used_seconds += 1
            self._update_display()
        else:
            self.timer.stop()
            self.countdown_val.setText("00:00")
            self.countdown_val.setStyleSheet("font-family: Consolas, monospace; font-size: 32px; font-weight: 700; color: #dc2626;")
            QMessageBox.warning(self, "Hết thời gian", "Đã hết hạn mức sử dụng máy tính hôm nay.")

    def _update_display(self):
        mins = self.remaining_seconds // 60
        secs = self.remaining_seconds % 60
        self.countdown_val.setText(f"{mins:02d}:{secs:02d}")

        if self.remaining_seconds <= 300:
            self.countdown_val.setStyleSheet("font-family: Consolas, monospace; font-size: 32px; font-weight: 700; color: #d97706;")

        pct = min(100, int((self.used_seconds / self.total_quota_seconds) * 100))
        self.progress_bar.setValue(pct)

        u_hrs = self.used_seconds // 3600
        u_mins = (self.used_seconds % 3600) // 60
        self.quota_desc.setText(f"Đã dùng {u_hrs}h {u_mins:02d}m trên hạn mức 2h 00m ({pct}%)")

    def _open_request_dialog(self):
        dlg = RequestTimeDialog(self)
        dlg.exec()

    def _open_report_dialog(self):
        dlg = ReportBlockedDialog(self)
        dlg.exec()

    def _open_blocked_dialog(self):
        dlg = BlockedListDialog(self)
        dlg.exec()