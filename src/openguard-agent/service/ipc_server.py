import json
import threading
import win32pipe
import win32file
import pywintypes

PIPE_NAME = r"\\.\pipe\openguard_ipc"
BUFFER_SIZE = 4096


class IpcPipeServer:
    def __init__(self, on_request_callback=None):
        self.on_request_callback = on_request_callback
        self._running = False
        self._pipe_handle = None
        self._connected = False
        self._lock = threading.Lock()

    def start(self):
        self._running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        while self._running:
            try:
                # Tạo Named Pipe Server hai chiều
                self._pipe_handle = win32pipe.CreateNamedPipe(
                    PIPE_NAME,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1,
                    BUFFER_SIZE,
                    BUFFER_SIZE,
                    0,
                    None
                )

                print("[IPC SERVER] Đang chờ kết nối từ TrayUI...")
                win32pipe.ConnectNamedPipe(self._pipe_handle, None)
                self._connected = True
                print("[IPC SERVER] TrayUI đã kết nối thành công!")

                # Đọc yêu cầu gửi từ UI
                while self._running and self._connected:
                    try:
                        hr, data = win32file.ReadFile(self._pipe_handle, BUFFER_SIZE)
                        if hr == 0 and data:
                            msg = json.loads(data.decode("utf-8"))
                            self._handle_incoming_message(msg)
                    except pywintypes.error:
                        # Client đã ngắt kết nối
                        break

            except Exception as e:
                print(f"[IPC SERVER] Lỗi pipe: {e}")
            finally:
                self._connected = False
                if self._pipe_handle:
                    try:
                        win32pipe.DisconnectNamedPipe(self._pipe_handle)
                        win32file.CloseHandle(self._pipe_handle)
                    except Exception:
                        pass

    def _handle_incoming_message(self, msg: dict):
        msg_type = msg.get("type")
        if msg_type == "REQUEST_TIME":
            print(f"[IPC IN] Bé xin thêm {msg.get('minutes')} phút: \"{msg.get('reason')}\"")
            if self.on_request_callback:
                self.on_request_callback("REQUEST_TIME", msg)
        elif msg_type == "REPORT_BLOCKED":
            print(f"[IPC IN] Bé báo nhầm web: {msg.get('domain')}")
            if self.on_request_callback:
                self.on_request_callback("REPORT_BLOCKED", msg)

    def broadcast_status(self, used_sec: int, remaining_sec: int, quota_sec: int):
        if not self._connected or not self._pipe_handle:
            return

        payload = {
            "type": "STATUS_TICK",
            "used_sec": used_sec,
            "remaining_sec": remaining_sec,
            "quota_sec": quota_sec,
        }

        try:
            with self._lock:
                data = json.dumps(payload).encode("utf-8")
                win32file.WriteFile(self._pipe_handle, data)
        except pywintypes.error:
            self._connected = False