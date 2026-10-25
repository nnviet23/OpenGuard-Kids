from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit import write_audit
from app.core.config import settings
from app.core.database import get_db, utcnow
from app.core.deps import AuthContext, get_auth
from app.core.ratelimit import client_ip, login_rate_limit
from app.core.security import (decrypt_field, encrypt_field, hash_password, new_token, new_totp_secret,
                               password_needs_rehash, token_hash, validate_password, verify_password, verify_totp)
from app.models import Account, WebSession

router = APIRouter(prefix="/auth", tags=["auth"])
GENERIC_FAIL = "Email hoặc mật khẩu không đúng"


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=256)
    display_name: str = Field(default="", max_length=100)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=256)
    totp: str | None = Field(default=None, max_length=8)


def account_out(a: Account) -> dict:
    return {"id": a.id, "email": a.email, "display_name": a.display_name, "role": a.role,
            "linked_child_id": a.linked_child_id, "totp_enabled": a.totp_enabled}


@router.post("/register", status_code=201, dependencies=[Depends(login_rate_limit)])
def register(body: RegisterIn, request: Request, db: Session = Depends(get_db)):
    errs = validate_password(body.password)
    if errs:
        raise HTTPException(422, "; ".join(errs))
    email = body.email.lower()
    if db.execute(select(Account).where(Account.email == email)).scalar_one_or_none():
        raise HTTPException(409, "Email đã được đăng ký")
    acc = Account(email=email, display_name=body.display_name or email.split("@")[0],
                  password_hash=hash_password(body.password), role="parent")
    db.add(acc)
    db.flush()
    write_audit(db, "account_registered", actor_type="parent", actor_id=acc.id, actor_name=acc.display_name,
                ip=client_ip(request))
    db.commit()
    return account_out(acc)


@router.post("/login", dependencies=[Depends(login_rate_limit)])
def login(body: LoginIn, request: Request, response: Response, db: Session = Depends(get_db)):
    ip = client_ip(request)
    acc = db.execute(select(Account).where(Account.email == body.email.lower())).scalar_one_or_none()
    now = utcnow()
    if acc and acc.locked_until and acc.locked_until > now:
        verify_password(body.password, None)  # giữ thời gian phản hồi đồng đều
        raise HTTPException(423, f"Tài khoản tạm khóa {settings.LOGIN_LOCK_MINUTES} phút do đăng nhập sai nhiều lần")
    ok = verify_password(body.password, acc.password_hash if acc else None)
    if ok and acc and acc.totp_enabled:
        counter = verify_totp(decrypt_field(acc.totp_secret_enc), body.totp or "", acc.totp_last_counter)
        if counter is None:
            ok = False
        else:
            acc.totp_last_counter = counter
    if not ok or not acc:
        if acc:
            acc.failed_attempts += 1
            if acc.failed_attempts >= settings.LOGIN_MAX_FAILURES:
                acc.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
                acc.failed_attempts = 0
                write_audit(db, "account_locked", actor_type="system", actor_id=acc.id, ip=ip)
            db.commit()
        raise HTTPException(401, GENERIC_FAIL)
    acc.failed_attempts, acc.locked_until = 0, None
    if password_needs_rehash(acc.password_hash):
        acc.password_hash = hash_password(body.password)
    raw, csrf = new_token(), new_token(24)
    db.add(WebSession(id_hash=token_hash(raw), account_id=acc.id, csrf_token=csrf, ip=ip,
                      expires_at=now + timedelta(seconds=settings.SESSION_TTL_SECONDS)))
    write_audit(db, "login", actor_type=acc.role, actor_id=acc.id, actor_name=acc.display_name, ip=ip)
    db.commit()
    response.set_cookie(settings.SESSION_COOKIE_NAME, raw, max_age=settings.SESSION_TTL_SECONDS, httponly=True,
                        secure=settings.COOKIE_SECURE or settings.ENV == "prod", samesite="lax", path="/")
    response.set_cookie(settings.CSRF_COOKIE_NAME, csrf, max_age=settings.SESSION_TTL_SECONDS, httponly=False,
                        secure=settings.COOKIE_SECURE or settings.ENV == "prod", samesite="lax", path="/")
    return {"account": account_out(acc), "csrf_token": csrf}


@router.post("/logout")
def logout(response: Response, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    ctx.session.revoked = True  # vô hiệu hóa phía server, không chỉ xóa cookie
    db.add(ctx.session)
    db.commit()
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
    response.delete_cookie(settings.CSRF_COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me")
def me(ctx: AuthContext = Depends(get_auth)):
    return {"account": account_out(ctx.account), "csrf_token": ctx.session.csrf_token}


class PwChange(BaseModel):
    current_password: str = Field(max_length=256)
    new_password: str = Field(max_length=256)


@router.post("/password")
def change_password(body: PwChange, request: Request, ctx: AuthContext = Depends(get_auth),
                    db: Session = Depends(get_db)):
    acc = ctx.account
    if not verify_password(body.current_password, acc.password_hash):
        raise HTTPException(401, "Mật khẩu hiện tại không đúng")
    errs = validate_password(body.new_password)
    if errs:
        raise HTTPException(422, "; ".join(errs))
    acc.password_hash = hash_password(body.new_password)
    for s in db.execute(select(WebSession).where(WebSession.account_id == acc.id,
                                                 WebSession.id_hash != ctx.session.id_hash)).scalars():
        s.revoked = True  # đăng xuất mọi phiên khác
    write_audit(db, "password_changed", actor_type=acc.role, actor_id=acc.id, actor_name=acc.display_name,
                ip=client_ip(request))
    db.commit()
    return {"ok": True}


@router.post("/totp/setup")
def totp_setup(ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    acc = ctx.account
    if acc.totp_enabled:
        raise HTTPException(409, "TOTP đã bật")
    secret = new_totp_secret()
    acc.totp_secret_enc = encrypt_field(secret)  # AES-GCM
    db.commit()
    return {"secret": secret, "otpauth_uri": f"otpauth://totp/OpenGuardKids:{acc.email}?secret={secret}&issuer=OpenGuardKids"}


class TotpCode(BaseModel):
    code: str = Field(max_length=8)
    password: str | None = Field(default=None, max_length=256)


@router.post("/totp/enable")
def totp_enable(body: TotpCode, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    acc = ctx.account
    if not acc.totp_secret_enc:
        raise HTTPException(409, "Chưa khởi tạo TOTP")
    counter = verify_totp(decrypt_field(acc.totp_secret_enc), body.code, acc.totp_last_counter)
    if counter is None:
        raise HTTPException(422, "Mã không đúng")
    acc.totp_enabled, acc.totp_last_counter = True, counter
    write_audit(db, "totp_enabled", actor_type=acc.role, actor_id=acc.id, actor_name=acc.display_name)
    db.commit()
    return {"ok": True}


@router.post("/totp/disable")
def totp_disable(body: TotpCode, ctx: AuthContext = Depends(get_auth), db: Session = Depends(get_db)):
    acc = ctx.account
    if not body.password or not verify_password(body.password, acc.password_hash):
        raise HTTPException(401, "Cần nhập đúng mật khẩu để tắt TOTP")
    acc.totp_enabled, acc.totp_secret_enc = False, None
    write_audit(db, "totp_disabled", actor_type=acc.role, actor_id=acc.id, actor_name=acc.display_name)
    db.commit()
    return {"ok": True}
