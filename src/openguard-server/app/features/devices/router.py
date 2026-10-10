from fastapi import APIRouter
from datetime import datetime, timezone
from app.features.devices.schemas import HeartbeatPayload, HeartbeatResponse

router = APIRouter(prefix="/agent", tags=["Agent Communications"])

# Mock phiên bản chính sách mới nhất trên Server
CURRENT_SERVER_POLICY_VERSION = 1


@router.post("/heartbeat", response_model=HeartbeatResponse)
def receive_heartbeat(payload: HeartbeatPayload):
    """
    Tiếp nhận nhịp tim định kỳ 60s từ Agent, kiểm tra phiên bản chính sách
    và gửi về danh sách lệnh khẩn đang chờ (nếu có).
    """
    # Ghi nhận log nhận heartbeat
    print(
        f"[HEARTBEAT] Nhận từ {payload.device_id}: Đã dùng {payload.used_screen_time_sec}s, Policy v{payload.policy_version}")

    return HeartbeatResponse(
        status="ok",
        server_time=datetime.now(timezone.utc),
        latest_policy_version=CURRENT_SERVER_POLICY_VERSION,
        pending_commands=[]
    )
