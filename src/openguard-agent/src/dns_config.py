"""Cấu hình DNS hệ thống trỏ về 127.0.0.1 và phát hiện/khôi phục khi bị đổi lại (F2 – đối phó đổi DNS).

Không có cơ chế chống gỡ: `restore()` luôn trả lại DNS tự động (DHCP) khi gỡ cài đặt/ngừng ghép cặp.
"""
from __future__ import annotations

import re
import subprocess
import sys
from typing import Callable

Runner = Callable[[list[str]], str]


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=20, check=False).stdout


def parse_netsh_dns(output: str) -> dict[str, list[str]]:
    """Phân tích `netsh interface ip show dnsservers` -> {interface: [dns,...]}."""
    result: dict[str, list[str]] = {}
    current = None
    for line in output.splitlines():
        m = re.search(r'(?:interface|giao diện)\s+"([^"]+)"', line, re.I)
        if m:
            current = m.group(1)
            result[current] = []
            continue
        for ip in re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", line):
            if current is not None:
                result[current].append(ip)
    return result


class DnsGuard:
    def __init__(self, interfaces: list[str] | None = None, runner: Runner = _run, enabled: bool = True) -> None:
        self.interfaces, self.run, self.enabled = interfaces, runner, enabled and sys.platform == "win32"
        if runner is not _run:
            self.enabled = enabled  # cho phép test với runner giả trên mọi nền tảng

    def current(self) -> dict[str, list[str]]:
        return parse_netsh_dns(self.run(["netsh", "interface", "ip", "show", "dnsservers"]))

    def apply(self) -> list[str]:
        changed = []
        if not self.enabled:
            return changed
        for iface in (self.interfaces or list(self.current())):
            self.run(["netsh", "interface", "ip", "set", "dnsservers", f"name={iface}", "static", "127.0.0.1", "primary"])
            changed.append(iface)
        return changed

    def check_and_repair(self) -> list[str]:
        """Trả danh sách giao diện bị đổi DNS (và đã sửa lại)."""
        if not self.enabled:
            return []
        drifted = [i for i, servers in self.current().items()
                   if (self.interfaces is None or i in self.interfaces) and servers[:1] != ["127.0.0.1"]]
        for iface in drifted:
            self.run(["netsh", "interface", "ip", "set", "dnsservers", f"name={iface}", "static", "127.0.0.1", "primary"])
        return drifted

    def restore(self) -> None:
        if not self.enabled:
            return
        for iface in (self.interfaces or list(self.current())):
            self.run(["netsh", "interface", "ip", "set", "dnsservers", f"name={iface}", "dhcp"])
