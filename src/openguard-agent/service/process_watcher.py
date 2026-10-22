import os
import hashlib
import psutil
from typing import Dict, List, Set, Tuple


class ProcessWatcher:
    """Giám sát tiến trình Windows và phát hiện phần mềm bị đổi tên qua SHA-256."""

    def __init__(self, blocked_hashes: Set[str] = None, blocked_names: Set[str] = None):
        # Tập hợp mã băm SHA-256 viết thường của các file thực thi bị chặn
        self.blocked_hashes = blocked_hashes or {
            # Ví dụ: mã băm SHA-256 mẫu của game/phần mềm không phù hợp
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        
        # Danh sách tên file thực thi mặc định cần chặn
        self.blocked_names = {name.lower() for name in (blocked_names or {
            "robloxplayer.exe",
            "robloxplayerlauncher.exe",
            "discord.exe",
        })}

        # Cache băm: {filepath: (mtime, sha256_hash)}
        self._hash_cache: Dict[str, Tuple[float, str]] = {}
        self.killed_events: List[dict] = []

    def _compute_sha256(self, filepath: str) -> str:
        """Tính SHA-256 của file thực thi với cơ chế bộ nhớ đệm theo mtime."""
        try:
            stat = os.stat(filepath)
            mtime = stat.st_mtime

            if filepath in self._hash_cache:
                cached_mtime, cached_hash = self._hash_cache[filepath]
                if cached_mtime == mtime:
                    return cached_hash

            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)

            file_hash = hasher.hexdigest().lower()
            self._hash_cache[filepath] = (mtime, file_hash)
            return file_hash
        except (PermissionError, FileNotFoundError, OSError):
            return ""

    def scan_and_enforce(self) -> List[dict]:
        """Quét toàn bộ tiến trình người dùng, ngắt các app vi phạm và trả về log."""
        violations = []

        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                name = (proc.info.get("name") or "").lower()
                exe_path = proc.info.get("exe") or ""

                if not exe_path or not name:
                    continue

                is_violation = False
                reason = ""

                # 1. Kiểm tra theo tên file thực thi
                if name in self.blocked_names:
                    is_violation = True
                    reason = f"Blocked Process Name ({name})"

                # 2. Kiểm tra theo SHA-256 nếu app bị đổi tên file
                if not is_violation and exe_path:
                    proc_hash = self._compute_sha256(exe_path)
                    if proc_hash and proc_hash in self.blocked_hashes:
                        is_violation = True
                        reason = f"Blocked SHA-256 Signature ({proc_hash[:8]}...)"

                if is_violation:
                    pid = proc.info["pid"]
                    proc.kill()  # Cưỡng chế ngắt tiến trình ngay lập tức

                    event = {
                        "pid": pid,
                        "name": name,
                        "path": exe_path,
                        "reason": reason,
                    }
                    violations.append(event)
                    self.killed_events.append(event)
                    print(f"[PROCESS WATCHER] KILLED: {name} (PID: {pid}) - Lý do: {reason}")

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return violations