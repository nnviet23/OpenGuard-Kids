
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_parent
from app.features.policies.schemas import (
    QuotaResponse,
    QuotaUpdateRequest,
    ScheduleResponse,
    ScheduleUpdateRequest,
)
from app.models.device import Device
from app.models.device_policy import DevicePolicy
from app.models.device_schedule import DeviceSchedule

router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


def get_owned_device(
    device_id: str,
    parent_id: str,
    db: Session,
) -> Device:
    device = (
        db.query(Device)
        .filter(
            Device.id == device_id,
            Device.parent_id == parent_id,
        )
        .first()
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device

#GET

@router.get(
    "/{device_id}/quota",
    response_model=QuotaResponse,
)
def get_quota(
    device_id: str,
    current_parent: dict = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    device = get_owned_device(
        device_id=device_id,
        parent_id=current_parent["parent_id"],
        db=db,
    )

    policy = (
        db.query(DevicePolicy)
        .filter(DevicePolicy.device_id == device.id)
        .first()
    )

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quota policy not found",
        )

    return QuotaResponse(
        device_id=device.id,
        weekday_limit_minutes=policy.weekday_limit_minutes,
        weekend_limit_minutes=policy.weekend_limit_minutes,
        enabled=policy.enabled,
        policy_version=policy.version,
    )

#PUT

@router.put(
    "/{device_id}/quota",
    response_model=QuotaResponse,
)
def update_quota(
    device_id: str,
    request: QuotaUpdateRequest,
    current_parent: dict = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    device = get_owned_device(
        device_id=device_id,
        parent_id=current_parent["parent_id"],
        db=db,
    )

    policy = (
        db.query(DevicePolicy)
        .filter(DevicePolicy.device_id == device.id)
        .first()
    )

    if policy is None:
        policy = DevicePolicy(
            device_id=device.id,
            weekday_limit_minutes=request.weekday_limit_minutes,
            weekend_limit_minutes=request.weekend_limit_minutes,
            enabled=request.enabled,
            version=1,
        )
        db.add(policy)
        db.flush()
        device.policy_version = policy.version

    else:
        changed = (
            policy.weekday_limit_minutes != request.weekday_limit_minutes
            or policy.weekend_limit_minutes != request.weekend_limit_minutes
            or policy.enabled != request.enabled
        )

        if changed:
            policy.weekday_limit_minutes = request.weekday_limit_minutes
            policy.weekend_limit_minutes = request.weekend_limit_minutes
            policy.enabled = request.enabled
            policy.version += 1
            device.policy_version = policy.version

    try:
        db.commit()
        db.refresh(policy)
    except Exception:
        db.rollback()
        raise

    return QuotaResponse(
        device_id=device.id,
        weekday_limit_minutes=policy.weekday_limit_minutes,
        weekend_limit_minutes=policy.weekend_limit_minutes,
        enabled=policy.enabled,
        policy_version=policy.version,
    )


# GET weekly schedule
@router.get(
    "/{device_id}/schedule",
    response_model=ScheduleResponse,
)
def get_schedule(
    device_id: str,
    current_parent: dict = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    device = get_owned_device(
        device_id=device_id,
        parent_id=current_parent["parent_id"],
        db=db,
    )

    schedule_record = (
        db.query(DeviceSchedule)
        .filter(DeviceSchedule.device_id == device.id)
        .first()
    )

    # Chưa có lịch thì tạo lịch mặc định: chặn tất cả khung giờ
    if schedule_record is None:
        schedule_record = DeviceSchedule(device_id=device.id)
        db.add(schedule_record)
        db.commit()
        db.refresh(schedule_record)

    return ScheduleResponse(
        device_id=device.id,
        schedule=schedule_record.schedule,
        version=schedule_record.version,
    )


# PUT weekly schedule
@router.put(
    "/{device_id}/schedule",
    response_model=ScheduleResponse,
)
def update_schedule(
    device_id: str,
    request: ScheduleUpdateRequest,
    current_parent: dict = Depends(get_current_parent),
    db: Session = Depends(get_db),
):
    device = get_owned_device(
        device_id=device_id,
        parent_id=current_parent["parent_id"],
        db=db,
    )

    schedule_record = (
        db.query(DeviceSchedule)
        .filter(DeviceSchedule.device_id == device.id)
        .first()
    )

    if schedule_record is None:
        schedule_record = DeviceSchedule(
            device_id=device.id,
            schedule=request.schedule,
            version=1,
        )
        db.add(schedule_record)
    else:
        if schedule_record.schedule != request.schedule:
            schedule_record.schedule = request.schedule
            schedule_record.version += 1

    try:
        db.commit()
        db.refresh(schedule_record)
    except Exception:
        db.rollback()
        raise

    return ScheduleResponse(
        device_id=device.id,
        schedule=schedule_record.schedule,
        version=schedule_record.version,
    )
