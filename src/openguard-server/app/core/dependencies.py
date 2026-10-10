from fastapi import Request, HTTPException, status, Depends
from app.core.config import settings
from app.core.security import decode_jwt_token


async def get_current_parent(request: Request) -> dict:
    """
    Lấy và xác thực phiên đăng nhập của phụ huynh từ HttpOnly Cookie.
    """
    session_token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập hoặc phiên làm việc đã hết hạn",
        )

    payload = decode_jwt_token(session_token)
    if not payload or payload.get("role") != "parent":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên làm việc không hợp lệ",
        )

    return {
        "parent_id": payload.get("sub"),
        "role": payload.get("role")
    }
