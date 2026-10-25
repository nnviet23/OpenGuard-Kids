"""Kiểm soát ứng dụng theo tên + SHA-256; theo dõi app_start/app_stop; ngân sách theo nhóm ứng dụng."""
from __future__ import annotations

import hashlib
import ntpath
import os
import sys
from dataclasses import dataclass
from typing import Callable

SYSTEM_DIRS = ("c:\\windows\\", "c:\\program files\\windowsapps\\")
IGNORED_NAMES = {"system", "registry", "svchost.exe", "csrss.exe", "services.exe", "lsass.exe", "wininit.exe",
                 "winlogon.exe", "dwm.exe", "explorer.exe", "python.exe", "pythonw.exe", "openguard.exe",
                 "conhost.exe", "fontdrvhost.exe", "sihost.exe", "taskhostw.exe", "runtimebroker.exe"}


@dataclass(frozen=True)
class ProcInfo:
    pid: int
    name: str
    exe: str


def is_user_app(p: ProcInfo) -> bool:
    n = p.name.lower()
    if not n or n in IGNORED_NAMES:
        return False
    exe = (p.exe or "").lower().replace("/", "\\")
    return not any(exe.startswith(d) for d in SYSTEM_DIRS)


def sha256_file(path: str) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def list_processes() -> list[ProcInfo]:
    import psutil
    out = []
    for p in psutil.process_iter(["pid", "name", "exe"]):
        try:
            out.append(ProcInfo(p.info["pid"], p.info["name"] or "", p.info["exe"] or ""))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return out


def terminate_process(pid: int) -> bool:
    import psutil
    try:
        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(3)
        except psutil.TimeoutExpired:
            p.kill()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


class AppController:
    def __init__(self, lister: Callable[[], list[ProcInfo]] = list_processes,
                 hasher: Callable[[str], str | None] = sha256_file,
                 terminator: Callable[[int], bool] = terminate_process, enforce: bool = False,
                 mono: Callable[[], float] | None = None) -> None:
        import time
        self.lister, self.hasher, self.terminator, self.enforce = lister, hasher, terminator, enforce
        self._mono = mono or time.monotonic
        self._running: dict[int, tuple[str, float]] = {}
        self._hash_cache: dict[tuple[str, int], str | None] = {}
        self._last_scan = self._mono()

    def _hash(self, p: ProcInfo) -> str | None:
        if not p.exe:
            return None
        try:
            key = (p.exe, int(os.stat(p.exe).st_mtime_ns))
        except OSError:
            return self.hasher(p.exe)
        if key not in self._hash_cache:
            self._hash_cache[key] = self.hasher(p.exe)
        return self._hash_cache[key]

    @staticmethod
    def match_rule(p: ProcInfo, sha: str | None, rules: list[dict]) -> dict | None:
        """Chặn nếu trùng tên HOẶC trùng SHA-256 (đổi tên file vẫn bị bắt bởi băm)."""
        for r in rules:
            if r.get("action") != "block":  # allow/limit không bị chặn trực tiếp ("limit" chỉ tính vào ngân sách nhóm)
                continue
            if r.get("name", "").lower() == p.name.lower() or (r.get("sha256") and sha and r["sha256"].lower() == sha):
                return r
        return None

    def scan(self, policy: dict, user_active: bool = True, blocked_groups: list[str] | None = None) -> dict:
        """Trả {events:[(type, subject, duration, policy_id)], group_delta:{grp: sec}, blocked:[(name, why)]}."""
        now = self._mono()
        elapsed, self._last_scan = max(0.0, now - self._last_scan), now
        rules = policy.get("app_rules", []) or []
        pid = policy.get("policy_id", "v0")
        events, blocked, group_delta = [], [], {}
        procs = {p.pid: p for p in self.lister() if is_user_app(p)}

        for pid_, (name, started) in list(self._running.items()):
            if pid_ not in procs:
                events.append(("app_stop", name, int(now - started), pid))
                del self._running[pid_]

        group_of = {r.get("name", "").lower(): r.get("group") for r in rules if r.get("group")}
        for p in procs.values():
            sha = self._hash(p) if rules else None
            rule = self.match_rule(p, sha, rules)
            grp = group_of.get(p.name.lower())
            why = None
            if rule:
                why = f"{pid}:app:{rule.get('name') or p.name}"
            elif grp and blocked_groups and grp in blocked_groups:
                why = f"{pid}:group_budget:{grp}"
            if why:
                killed = self.terminator(p.pid) if self.enforce else False
                blocked.append((p.name, why, killed))
                events.append(("blocked_app", p.name, 0, why))
                continue
            if p.pid not in self._running:
                self._running[p.pid] = (p.name, now)
                events.append(("app_start", p.name, 0, pid))
            if grp and user_active:
                group_delta[grp] = group_delta.get(grp, 0.0) + elapsed
        return {"events": events, "group_delta": group_delta, "blocked": blocked}

    def close_all(self) -> list[tuple]:
        now = self._mono()
        ev = [("app_stop", n, int(now - s), "") for n, s in self._running.values()]
        self._running.clear()
        return ev
