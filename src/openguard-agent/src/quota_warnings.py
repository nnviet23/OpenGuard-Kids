"""Cảnh báo 10/5/1 phút và thời gian ân hạn 60 giây trước khi khóa vì hết hạn mức."""
from __future__ import annotations

WARNING_THRESHOLDS = (600, 300, 60)
GRACE_SECONDS = 60


class WarningScheduler:
    def __init__(self) -> None:
        self._fired: set[tuple[str, str, int]] = set()

    def due(self, date: str, cause: str | None, remaining: int | None) -> list[int]:
        """Trả danh sách ngưỡng (giây) cần cảnh báo ngay – mỗi ngưỡng chỉ một lần mỗi ngày/nguyên nhân."""
        if remaining is None or cause is None or remaining <= 0:
            return []
        out = []
        for t in WARNING_THRESHOLDS:
            key = (date, cause, t)
            # chỉ cảnh báo ngưỡng nhỏ nhất đã lọt vào (tránh bắn 3 lần khi vừa khởi động ở còn 30 giây)
            if remaining <= t and key not in self._fired:
                out.append(t)
        if out:
            smallest = min(out)
            for t in WARNING_THRESHOLDS:
                if t >= smallest:
                    self._fired.add((date, cause, t))
            return [smallest]
        return []

    def reset(self) -> None:
        self._fired.clear()


class GraceTimer:
    """Ân hạn khi hết hạn mức; hết lịch thì khóa ngay (đã cảnh báo 10/5/1 phút trước)."""

    def __init__(self, grace: int = GRACE_SECONDS) -> None:
        self.grace, self.started_at = grace, None

    def should_lock(self, now_mono: float, cause: str | None) -> bool:
        if cause in ("schedule", "forced"):
            self.started_at = None
            return True
        if cause != "quota":
            self.started_at = None
            return False
        if self.started_at is None:
            self.started_at = now_mono
        return now_mono - self.started_at >= self.grace

    def seconds_left(self, now_mono: float) -> int:
        return 0 if self.started_at is None else max(0, int(self.grace - (now_mono - self.started_at)))

    def clear(self) -> None:
        self.started_at = None
