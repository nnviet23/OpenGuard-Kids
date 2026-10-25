from datetime import datetime
from zoneinfo import ZoneInfo

from policy_checker import check_policy


VN = ZoneInfo("Asia/Ho_Chi_Minh")


def make_schedule(default=False):
    return [[default for _ in range(48)] for _ in range(7)]


def test_allowed_when_quota_and_schedule_allow():
    schedule = make_schedule()
    # Frontend stores Monday at index 0; 09:00 maps to slot 18.
    schedule[0][18] = True

    result = check_policy(
        quota={
            "weekday_limit_minutes": 180,
            "weekend_limit_minutes": 120,
            "enabled": True,
        },
        schedule=schedule,
        daily_used_seconds=600,
        now=datetime(2026, 10, 19, 9, 5, tzinfo=VN),  # Monday
    )

    assert result == "ALLOWED"


def test_quota_exceeded_at_exact_limit():
    schedule = make_schedule(True)

    result = check_policy(
        quota={
            "weekday_limit_minutes": 180,
            "weekend_limit_minutes": 120,
            "enabled": True,
        },
        schedule=schedule,
        daily_used_seconds=180 * 60,
        now=datetime(2026, 10, 19, 9, 5, tzinfo=VN),  # Monday
    )

    assert result == "QUOTA_EXCEEDED"


def test_weekend_uses_weekend_quota():
    schedule = make_schedule(True)

    result = check_policy(
        quota={
            "weekday_limit_minutes": 180,
            "weekend_limit_minutes": 30,
            "enabled": True,
        },
        schedule=schedule,
        daily_used_seconds=30 * 60,
        now=datetime(2026, 10, 24, 9, 5, tzinfo=VN),  # Saturday
    )

    assert result == "QUOTA_EXCEEDED"


def test_outside_allowed_schedule():
    schedule = make_schedule(False)

    result = check_policy(
        quota={
            "weekday_limit_minutes": 180,
            "weekend_limit_minutes": 120,
            "enabled": True,
        },
        schedule=schedule,
        daily_used_seconds=0,
        now=datetime(2026, 10, 19, 9, 5, tzinfo=VN),
    )

    assert result == "OUTSIDE_ALLOWED_SCHEDULE"


def test_disabled_policy():
    result = check_policy(
        quota={
            "weekday_limit_minutes": 180,
            "weekend_limit_minutes": 120,
            "enabled": False,
        },
        schedule=make_schedule(False),
        daily_used_seconds=0,
        now=datetime(2026, 10, 19, 9, 5, tzinfo=VN),
    )

    assert result == "POLICY_DISABLED"


def test_missing_schedule_is_invalid_policy():
    result = check_policy(
        quota={
            "weekday_limit_minutes": 180,
            "weekend_limit_minutes": 120,
            "enabled": True,
        },
        schedule=None,
        daily_used_seconds=0,
        now=datetime(2026, 10, 19, 9, 5, tzinfo=VN),
    )

    assert result == "INVALID_POLICY"


def test_malformed_schedule_is_invalid_policy():
    result = check_policy(
        quota={
            "weekday_limit_minutes": 180,
            "weekend_limit_minutes": 120,
            "enabled": True,
        },
        schedule=[[False] * 48 for _ in range(6)],
        daily_used_seconds=0,
        now=datetime(2026, 10, 19, 9, 5, tzinfo=VN),
    )

    assert result == "INVALID_POLICY"
