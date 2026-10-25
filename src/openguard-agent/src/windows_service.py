"""Dịch vụ Windows (chạy dưới tài khoản SYSTEM). Chỉ nạp trên Windows có pywin32."""
from __future__ import annotations

import sys
import threading

import servicemanager  # type: ignore
import win32event  # type: ignore
import win32service  # type: ignore
import win32serviceutil  # type: ignore

import main_service
from agent_core import AgentConfig


class OpenGuardService(win32serviceutil.ServiceFramework):
    _svc_name_ = "OpenGuardKids"
    _svc_display_name_ = "OpenGuard Kids Agent"
    _svc_description_ = "Giúp phụ huynh quản lý thời gian dùng máy của trẻ. Có biểu tượng hiển thị ở khay hệ thống; có thể gỡ bất cứ lúc nào."

    def __init__(self, args):
        super().__init__(args)
        self._stop = threading.Event()
        self._evt = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self._stop.set()
        win32event.SetEvent(self._evt)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("OpenGuard Kids starting")
        cfg = AgentConfig.from_env()
        core = main_service.build_core(cfg)
        main_service.start_background(core, cfg, self._stop)
        core.run_forever(self._stop)


def handle(action: str) -> int:
    argv = [sys.argv[0], "--startup=auto", "install"] if action == "install" else [sys.argv[0], action]
    win32serviceutil.HandleCommandLine(OpenGuardService, argv=argv)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(OpenGuardService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(OpenGuardService)
