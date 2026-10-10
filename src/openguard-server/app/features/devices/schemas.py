from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class HeartbeatPayload(BaseModel):
    device_id: str
    timestamp: datetime
    used_screen_time_sec: int = Field(ge=0)
    policy_version: int = Field(ge=1)
    agent_status: str = "active"


class HeartbeatResponse(BaseModel):
    status: str = "ok"
    server_time: datetime
    latest_policy_version: int
    pending_commands: List[str] = []
