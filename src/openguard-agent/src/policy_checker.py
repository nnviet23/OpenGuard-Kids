
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

LOCAL_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


def check_policy(
    quota: dict[str, Any] | None,
    schedule: list[list[bool]] | None,
    daily_used_seconds: int,
    now: datetime | None = None,
) -> str:
    """
    Kiểm tra chính sách, chưa thực hiện khóa máy.

    Trả về:
    - POLICY_DISABLED
    - QUOTA_EXCEEDED
    - OUTSIDE_ALLOWED_SCHEDULE
    - ALLOWED
    - INVALID_POLICY
    """
    if quota is None:
        return "INVALID_POLICY"

    if not quota.get("enabled", False):
        return "POLICY_DISABLED"

    if not isinstance(daily_used_seconds, int) or isinstance(daily_used_seconds, bool) or daily_used_seconds < 0:
        return "INVALID_POLICY"

    if now is None:
        now = datetime.now(LOCAL_TIMEZONE)
    elif now.tzinfo is None:
        # Tạm hiểu datetime không có timezone là giờ Việt Nam.
        now = now.replace(tzinfo=LOCAL_TIMEZONE)
    else:
        now = now.astimezone(LOCAL_TIMEZONE)

    # weekday(): Monday = 0, Sunday = 6.
    is_weekend = now.weekday() >= 5
    quota_key = (
        "weekend_limit_minutes"
        if is_weekend
        else "weekday_limit_minutes"
    )

    quota_minutes = quota.get(quota_key)

    if not isinstance(quota_minutes, int) or quota_minutes < 0:
        return "INVALID_POLICY"

    if daily_used_seconds >= quota_minutes * 60:
        return "QUOTA_EXCEEDED"

    # Không thể kiểm tra lịch nếu lịch chưa được đồng bộ.
    if schedule is None:
        return "INVALID_POLICY"

    if len(schedule) != 7 or any(
        not isinstance(day, list) or len(day) != 48
        or any(not isinstance(slot, bool) for slot in day)
        for day in schedule
    ):
        return "INVALID_POLICY"

    # Chỉ số ngày và khung giờ đang giả định:
    # Monday = 0; mỗi ngày có 48 khung 30 phút.
    day_index = now.weekday()
    slot_index = now.hour * 2 + (1 if now.minute >= 30 else 0)

    if not schedule[day_index][slot_index]:
        return "OUTSIDE_ALLOWED_SCHEDULE"

    return "ALLOWED"


# ---------------------------------------------------------------------------
# Đánh giá đầy đủ từ gói chính sách của server (hạn mức + thưởng giờ + lịch + khóa khẩn)
# ---------------------------------------------------------------------------
SLOT_SECONDS = 30 * 60


def _to_local(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(LOCAL_TIMEZONE)
    if now.tzinfo is None:
        return now.replace(tzinfo=LOCAL_TIMEZONE)
    return now.astimezone(LOCAL_TIMEZONE)


def seconds_until_schedule_block(schedule: list[list[bool]], now: datetime | None = None) -> int | None:
    """Số giây cho đến khi khung giờ được phép kết thúc; None nếu lịch cho phép suốt 24 giờ tới."""
    local = _to_local(now)
    day, slot = local.weekday(), local.hour * 2 + (1 if local.minute >= 30 else 0)
    into_slot = (local.minute % 30) * 60 + local.second
    total = SLOT_SECONDS - into_slot
    for step in range(1, 48 * 7):
        nd, ns = (day + (slot + step) // 48) % 7, (slot + step) % 48
        if not schedule[nd][ns]:
            return total
        total += SLOT_SECONDS
        if total > 24 * 3600:
            return None
    return None


def evaluate(policy: dict[str, Any] | None, used_seconds: int, now: datetime | None = None,
             group_seconds: dict[str, int] | None = None) -> dict[str, Any]:
    """Kết quả: status + remaining_seconds (giây còn lại tới khi bị khóa, nhỏ nhất của hạn mức và lịch)
    + cause ('quota'|'schedule'|None) + blocked_groups (nhóm ứng dụng hết ngân sách)."""
    if not policy:
        return {"status": "INVALID_POLICY", "remaining_seconds": None, "cause": None, "blocked_groups": []}
    local = _to_local(now)
    bonus = int(policy.get("bonus_seconds_today", 0) or 0)
    quota = {"enabled": policy.get("enabled", False),
             "weekday_limit_minutes": policy.get("weekday_limit_minutes"),
             "weekend_limit_minutes": policy.get("weekend_limit_minutes")}
    paused_until = policy.get("paused_until")
    if paused_until:
        try:
            if datetime.fromisoformat(paused_until) > local:
                return {"status": "POLICY_DISABLED", "remaining_seconds": None, "cause": "paused", "blocked_groups": []}
        except ValueError:
            pass
    if policy.get("forced_lock"):
        return {"status": "FORCED_LOCK", "remaining_seconds": 0, "cause": "forced", "blocked_groups": []}
    status = check_policy(quota, policy.get("schedule"), max(0, int(used_seconds) - bonus), local)
    limit_min = quota["weekend_limit_minutes"] if local.weekday() >= 5 else quota["weekday_limit_minutes"]
    remaining, cause = None, None
    if status == "ALLOWED":
        q_rem = limit_min * 60 + bonus - int(used_seconds)
        s_rem = seconds_until_schedule_block(policy["schedule"], local)
        remaining, cause = q_rem, "quota"
        if s_rem is not None and s_rem < q_rem:
            remaining, cause = s_rem, "schedule"
    elif status == "QUOTA_EXCEEDED":
        remaining, cause = 0, "quota"
    elif status == "OUTSIDE_ALLOWED_SCHEDULE":
        remaining, cause = 0, "schedule"
    blocked = []
    for grp, minutes in (policy.get("group_budgets") or {}).items():
        if (group_seconds or {}).get(grp, 0) >= int(minutes) * 60:
            blocked.append(grp)
    return {"status": status, "remaining_seconds": remaining, "cause": cause, "blocked_groups": blocked}
