
from pydantic import BaseModel, Field, model_validator


class QuotaUpdateRequest(BaseModel):
    weekday_limit_minutes: int = Field(ge=1, le=1440)
    weekend_limit_minutes: int = Field(ge=1, le=1440)
    enabled: bool = True


class QuotaResponse(BaseModel):
    device_id: str
    weekday_limit_minutes: int
    weekend_limit_minutes: int
    enabled: bool
    policy_version: int


# Added 17/10/2026: Weekly schedule (7 days × 48 slots)
class ScheduleUpdateRequest(BaseModel):
    schedule: list[list[bool]] = Field(
        ...,
        description="Lịch 7 ngày, mỗi ngày gồm 48 khung giờ 30 phút",
    )

    @model_validator(mode="after")
    def validate_schedule(self):
        if len(self.schedule) != 7:
            raise ValueError("Lịch phải có đúng 7 ngày")

        if any(len(day) != 48 for day in self.schedule):
            raise ValueError("Mỗi ngày phải có đúng 48 khung giờ")

        return self


class ScheduleResponse(BaseModel):
    device_id: str
    schedule: list[list[bool]]
    version: int
