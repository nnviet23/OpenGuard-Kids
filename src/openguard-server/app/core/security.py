from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.core.config import settings

# Sử dụng Argon2id với tham số mặc định bảo mật cao
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng thuật toán Argon2id (NIST SP 800-63B)."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu với chuỗi băm Argon2id."""
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


def create_jwt_token(subject: Union[str, Any], role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Sinh JWT Token có gắn thời gian hết hạn."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(seconds=settings.SESSION_COOKIE_MAX_AGE)

    payload = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[dict]:
    """Giải mã và kiểm tra tính hợp lệ của token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
