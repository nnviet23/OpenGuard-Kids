import json
import threading
import win32file
import pywintypes
from PyQt6.QtCore import QObject, pyqtSignal

PIPE_NAME = r"\\.\pipe\openguard_ipc"
BUFFER_SIZE = 4096


class IpcClientWorker(QObject):
    # Signals emitted to Qt UI thread
    status_updated = pyqtSignal(int, int, int)  # used_sec, remaining_sec, quota_sec
    connection_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._running = False
        self._pipe_handle = None
        self._lock = threading.Lock()

    def start(self):
        self._running = True
        threading.Thread(target=self._read_loop, daemon=True).start()

    def stop(self):
        self._running = False
        if self._pipe_handle:
            try:
                win32file.CloseHandle(self._pipe_handle)
            except Exception:
                pass

    def _read_loop(self):
        while self._running:
            try:
                self._pipe_handle = win32file.CreateFile(
                    PIPE_NAME,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None,
                )
                self.connection_changed.emit(True)

                while self._running:
                    hr, data = win32file.ReadFile(self._pipe_handle, BUFFER_SIZE)
                    if hr == 0 and data:
                        msg = json.loads(data.decode("utf-8"))
                        if msg.get("type") == "STATUS_TICK":
                            self.status_updated.emit(
                                msg.get("used_sec", 0),
                                msg.get("remaining_sec", 0),
                                msg.get("quota_sec", 7200),
                            )

            except pywintypes.error:
                self.connection_changed.emit(False)
                self._pipe_handle = None
                threading.Event().wait(2.0)

    def send_message(self, msg_type: str, data: dict):
        if not self._pipe_handle:
            return

        payload = {"type": msg_type, **data}
        try:
            with self._lock:
                encoded = json.dumps(payload).encode("utf-8")
                win32file.WriteFile(self._pipe_handle, encoded)
        except pywintypes.error:
            pass