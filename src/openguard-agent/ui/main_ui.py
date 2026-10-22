import os
import sys
import signal

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QDialog
from ui.tray_app import OpenGuardTray
from ui.dialogs import PairingDialog


def mock_verify_pin(pin: str) -> tuple[bool, str]:
    if pin == "123456":
        return True, ""
    return False, "Mã PIN không chính xác hoặc đã hết hạn (15 phút)."


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    sigint_timer = QTimer()
    sigint_timer.timeout.connect(lambda: None)
    sigint_timer.start(500)

    pairing_dialog = PairingDialog(on_submit_callback=mock_verify_pin)
    result = pairing_dialog.exec()

    if result != QDialog.DialogCode.Accepted:
        sys.exit(0)
        
    _tray = OpenGuardTray()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()