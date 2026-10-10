from fastapi import APIRouter, Response, HTTPException, status, Depends
from app.core.config import settings
from app.core.security import create_jwt_token, hash_password, verify_password
from app.core.dependencies import get_current_parent
from app.features.auth.schemas import LoginRequest, ParentInfoResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Cập nhật thành domain hợp lệ .com để vượt qua Pydantic email-validator
MOCK_PARENT_DB = {
    "parent@openguard.com": {
        "id": "par_e4a8b29c",
        "email": "parent@openguard.com",
        "hashed_password": hash_password("OpenGuard@2026"),
        "role": "parent"
    }
}


@router.post("/login")
def login(login_data: LoginRequest, response: Response):
    user = MOCK_PARENT_DB.get(login_data.email)
    print(f"--> [DEBUG] Email nhận được: '{login_data.email}'")
    print(f"--> [DEBUG] Tìm thấy user trong DB: {bool(user)}")
    if user:
        is_pw_valid = verify_password(
            login_data.password, user["hashed_password"])
        print(f"--> [DEBUG] Mật khẩu đúng không: {is_pw_valid}")
        if not is_pw_valid:
            print(f"--> [DEBUG] Password nhận vào: '{login_data.password}'")

    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )

    # Sinh session token
    session_token = create_jwt_token(subject=user["id"], role=user["role"])

    # Thiết lập HttpOnly Cookie chuẩn OWASP ASVS v4
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_token,
        max_age=settings.SESSION_COOKIE_MAX_AGE,
        httponly=True,
        secure=False,      # Đổi thành True khi chạy trên môi trường HTTPS thật
        samesite="lax",
        path="/"
    )

    return {"message": "Đăng nhập thành công", "parent_id": user["id"]}


@router.get("/me", response_model=ParentInfoResponse)
def get_current_user_info(current_user: dict = Depends(get_current_parent)):
    """Lấy thông tin phụ huynh đang đăng nhập qua Cookie."""
    return {
        "id": current_user["parent_id"],
        "email": "parent@openguard.com",
        "role": current_user["role"]
    }


@router.post("/logout")
def logout(response: Response):
    """Xóa Session Cookie và hủy phiên làm việc."""
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/"
    )
    return {"message": "Đăng xuất thành công"}
