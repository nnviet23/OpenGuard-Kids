import threading

import win32gui
import win32ts

WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8


class LockMonitor:
    """Monitor Windows session lock and unlock events."""

    def __init__(self) -> None:
        self._locked = False
        self._ready = threading.Event()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

    @property
    def is_locked(self) -> bool:
        return self._locked

    def start(self) -> None:
        self._thread.start()

        if not self._ready.wait(timeout=5):
            raise RuntimeError("Lock monitor failed to start")

    def _run(self) -> None:
        class_name = "OpenGuardLockMonitor"

        wc = win32gui.WNDCLASS()
        wc.lpszClassName = class_name
        wc.lpfnWndProc = self._window_proc

        try:
            class_atom = win32gui.RegisterClass(wc)
            hwnd = win32gui.CreateWindow(
                class_atom,
                class_name,
                0,
                0, 0, 0, 0,
                0, 0, wc.hInstance, None,
            )

            win32ts.WTSRegisterSessionNotification(
                hwnd,
                win32ts.NOTIFY_FOR_THIS_SESSION,
            )

            self._ready.set()
            win32gui.PumpMessages()

        except Exception:
            self._ready.set()
            raise

    def _window_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_WTSSESSION_CHANGE:
            if wparam == WTS_SESSION_LOCK:
                self._locked = True
            elif wparam == WTS_SESSION_UNLOCK:
                self._locked = False

        return win32gui.DefWindowProc(
            hwnd, msg, wparam, lparam
        )
