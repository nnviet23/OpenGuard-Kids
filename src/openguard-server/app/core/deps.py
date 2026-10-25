"""Xác thực/ủy quyền: phiên cookie + CSRF cho web, bearer token cho thiết bị.

IDOR được chặn ở mức truy vấn: mọi truy vấn trẻ/thiết bị đều lọc theo chủ sở hữu và trả 404
(không phải 403) để không lộ sự tồn tại của tài nguyên của người khác.
"""
from __future__ import annotations

import hmac
from datetime import timedelta

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, utcnow
from app.core.security import decode_device_access_token, token_hash
from app.models import Account, Child, Device, WebSession

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class AuthContext:
    def __init__(self, account: Account, session: WebSession):
        self.account, self.session = account, session


def get_auth(request: Request, db: Session = Depends(get_db)) -> AuthContext:
    raw = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not raw:
        raise HTTPException(401, "Chưa đăng nhập")
    sess = db.get(WebSession, token_hash(raw))
    if not sess or sess.revoked or sess.expires_at <= utcnow():
        raise HTTPException(401, "Phiên đã hết hạn")
    account = db.get(Account, sess.account_id)
    if not account:
        raise HTTPException(401, "Phiên không hợp lệ")
    if request.method not in SAFE_METHODS:
        sent = request.headers.get("x-csrf-token", "")
        if not sent or not hmac.compare_digest(sent, sess.csrf_token):
            raise HTTPException(403, "CSRF token không hợp lệ")
    return AuthContext(account, sess)


def require_parent(ctx: AuthContext = Depends(get_auth)) -> Account:
    if ctx.account.role != "parent":
        raise HTTPException(403, "Chỉ phụ huynh được thực hiện thao tác này")
    return ctx.account


def require_admin(ctx: AuthContext = Depends(get_auth)) -> Account:
    if ctx.account.role != "admin":
        raise HTTPException(403, "Chỉ quản trị viên")
    return ctx.account


def owner_id_of(account: Account) -> str | None:
    """Id phụ huynh sở hữu dữ liệu mà tài khoản này được phép thấy."""
    if account.role == "parent":
        return account.id
    if account.role == "child_view":
        return account.owner_id
    return None  # admin: không có quyền xem dữ liệu của trẻ (tối thiểu hóa dữ liệu)


def scoped_child(db: Session, account: Account, child_id: str, *, write: bool = False) -> Child:
    q = select(Child).where(Child.id == child_id)
    if account.role == "parent":
        q = q.where(Child.parent_id == account.id)
    elif account.role == "child_view" and not write:
        q = q.where(Child.id == account.linked_child_id, Child.parent_id == account.owner_id)
    else:
        raise HTTPException(404, "Không tìm thấy")
    child = db.execute(q).scalar_one_or_none()
    if not child:
        raise HTTPException(404, "Không tìm thấy")
    return child


def scoped_device(db: Session, parent: Account, device_id: str) -> Device:
    dev = db.execute(select(Device).where(Device.id == device_id, Device.parent_id == parent.id)).scalar_one_or_none()
    if not dev:
        raise HTTPException(404, "Không tìm thấy")
    return dev


def get_device(request: Request, db: Session = Depends(get_db)) -> Device:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(401, "Thiếu token thiết bị")
    data = decode_device_access_token(auth[7:].strip())
    if not data:
        raise HTTPException(401, "Token thiết bị không hợp lệ hoặc đã hết hạn")
    dev = db.get(Device, data["sub"])
    if not dev or dev.status != "active":
        raise HTTPException(401, "Thiết bị đã bị thu hồi")
    return dev
