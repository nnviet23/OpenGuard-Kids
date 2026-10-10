from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    # Độ dài mật khẩu tối thiểu 10 ký tự theo chuẩn NIST SP 800-63B
    password: str = Field(..., min_length=10)


class ParentInfoResponse(BaseModel):
    id: str
    email: str
    role: str
