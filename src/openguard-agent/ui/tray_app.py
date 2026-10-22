from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from ui.activity_window import ActivitySummaryWindow


def make_simple_tray_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor("transparent"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#0e8368"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 28, 28, 4, 4)

    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "OG")
    painter.end()
    return QIcon(pixmap)


class OpenGuardTray(QWidget):
    def __init__(self):
        super().__init__()
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(make_simple_tray_icon())
        self.tray_icon.setToolTip("OpenGuard Kids")
        self.tray_icon.activated.connect(self._on_tray_activated)

        self.activity_window = ActivitySummaryWindow(self)

        self._build_context_menu()
        self.tray_icon.show()
        self.show_activity_summary()

        self.tray_icon.showMessage(
            "OpenGuard Kids",
            "Phần mềm đang hoạt động tại khay hệ thống.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def _build_context_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                padding: 5px 16px;
                color: #0f172a;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #0e8368;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e2e8f0;
                margin: 4px 0;
            }
        """)

        act_open = QAction("Hoạt động hôm nay", self)
        font = act_open.font()
        font.setBold(True)
        act_open.setFont(font)
        act_open.triggered.connect(self.show_activity_summary)
        menu.addAction(act_open)

        act_status = QAction("Thời lượng: 1h 45m / 2h 00m", self)
        act_status.setEnabled(False)
        menu.addAction(act_status)

        menu.addSeparator()

        act_req = QAction("Xin thêm giờ...", self)
        act_req.triggered.connect(self.activity_window._open_request_dialog)
        menu.addAction(act_req)

        act_rep = QAction("Báo nhầm trang...", self)
        act_rep.triggered.connect(self.activity_window._open_report_dialog)
        menu.addAction(act_rep)

        act_list = QAction("Danh sách hạn chế...", self)
        act_list.triggered.connect(self.activity_window._open_blocked_dialog)
        menu.addAction(act_list)

        menu.addSeparator()

        act_exit = QAction("Thoát (Dev Mode)", self)
        act_exit.triggered.connect(QApplication.instance().quit)
        menu.addAction(act_exit)

        self.tray_icon.setContextMenu(menu)

    def show_activity_summary(self):
        self.activity_window.show()
        self.activity_window.raise_()
        self.activity_window.activateWindow()

    def _on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_activity_summary()