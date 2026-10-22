
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.devices.schemas import (
    HeartbeatPayload,
    HeartbeatResponse,
)
from app.models.device import Device
from app.models.device_daily_usage import DeviceDailyUsage
from app.models.device_policy import DevicePolicy
from app.models.device_schedule import DeviceSchedule

router = APIRouter(
    prefix="/agent",
    tags=["Agent Communications"],
)

CURRENT_SERVER_POLICY_VERSION = 1

# Dùng múi giờ Việt Nam để xác định ngày sử dụng.
LOCAL_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


@router.post(
    "/heartbeat",
    response_model=HeartbeatResponse,
)
def receive_heartbeat(
    payload: HeartbeatPayload,
    db: Session = Depends(get_db),
):
    device = db.get(Device, payload.device_id)

    if device is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{payload.device_id}' not found",
        )

    now = datetime.now(timezone.utc)
    usage_date = now.astimezone(LOCAL_TIMEZONE).date()

    # Tính phần thời gian tăng thêm trong phiên hiện tại.
    additional_seconds = 0

    if device.agent_session_id == payload.session_id:
        previous_seconds = device.agent_last_reported_usage_sec

        if payload.used_screen_time_sec >= previous_seconds:
            additional_seconds = (
                payload.used_screen_time_sec - previous_seconds
            )
    else:
        # Agent bắt đầu một phiên mới.
        # Không lấy bộ đếm phiên mới trừ bộ đếm phiên cũ.
        additional_seconds = payload.used_screen_time_sec

    try:
        # Cập nhật thông tin Agent.
        device.last_seen_at = now
        device.used_screen_time_sec = payload.used_screen_time_sec
        device.agent_session_id = payload.session_id
        device.agent_last_reported_usage_sec = (
            payload.used_screen_time_sec
        )

        # Tìm bản ghi tổng thời gian của thiết bị trong ngày.
        daily_usage = (
            db.query(DeviceDailyUsage)
            .filter(
                DeviceDailyUsage.device_id == payload.device_id,
                DeviceDailyUsage.usage_date == usage_date,
            )
            .with_for_update()
            .first()
        )

        if daily_usage is None:
            daily_usage = DeviceDailyUsage(
                device_id=payload.device_id,
                usage_date=usage_date,
                used_seconds=0,
                updated_at=now,
            )
            db.add(daily_usage)

        daily_usage.used_seconds += additional_seconds
        daily_usage.updated_at = now

        db.commit()
        db.refresh(device)
        db.refresh(daily_usage)

    except Exception:
        db.rollback()
        raise

    print(
        f"[DB CHECK] device={device.id}, "
        f"latest_agent_counter={device.used_screen_time_sec}s, "
        f"daily_total={daily_usage.used_seconds}s"
    )

    print(
        f"[HEARTBEAT] Received from {payload.device_id}: "
        f"session={payload.session_id}, "
        f"reported={payload.used_screen_time_sec}s, "
        f"added={additional_seconds}s, "
        f"daily_total={daily_usage.used_seconds}s"
    )


    # Lấy chính sách quota của thiết bị.
    policy = (
        db.query(DevicePolicy)
        .filter(DevicePolicy.device_id == device.id)
        .first()
    )

    # Lấy lịch sử dụng trong tuần.
    schedule_record = (
        db.query(DeviceSchedule)
        .filter(DeviceSchedule.device_id == device.id)
        .first()
    )

    # Chỉ gửi quota khi thiết bị đã có chính sách.
    quota = None
    policy_version = CURRENT_SERVER_POLICY_VERSION

    if policy is not None:
        quota = {
            "weekday_limit_minutes": policy.weekday_limit_minutes,
            "weekend_limit_minutes": policy.weekend_limit_minutes,
            "enabled": policy.enabled,
        }
        policy_version = policy.version

    # Chỉ gửi lịch khi đã có bản ghi lịch tuần.
    schedule = None
    schedule_version = None

    if schedule_record is not None:
        schedule = schedule_record.schedule
        schedule_version = schedule_record.version

    return HeartbeatResponse(
        status="ok",
        server_time=now,
        latest_policy_version=policy_version,
        pending_commands=[],
        quota=quota,
        schedule=schedule,
        schedule_version=schedule_version,
    )
