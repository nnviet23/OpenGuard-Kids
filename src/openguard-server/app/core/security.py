"""Mật khẩu, khóa dẫn xuất, mã hóa trường nhạy cảm, ký chính sách, token thiết bị, TOTP."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import struct
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.core.config import settings

_ph = PasswordHasher()  # Argon2id mặc định
_DUMMY_HASH = _ph.hash("dummy-password-for-timing")
ENROLL_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # bỏ ký tự dễ nhầm I,O,0,1


# ---------- mật khẩu ----------
def validate_password(pw: str) -> list[str]:
    errs = []
    if len(pw) < settings.PASSWORD_MIN_LENGTH:
        errs.append(f"Mật khẩu phải có ít nhất {settings.PASSWORD_MIN_LENGTH} ký tự")
    if pw.lower() == pw or pw.upper() == pw or not any(c.isdigit() for c in pw):
        errs.append("Mật khẩu cần có chữ hoa, chữ thường và chữ số")
    return errs


def hash_password(pw: str) -> str:
    return _ph.hash(pw)


def verify_password(pw: str, hashed: str | None) -> bool:
    try:
        return _ph.verify(hashed or _DUMMY_HASH, pw) and hashed is not None
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def password_needs_rehash(hashed: str) -> bool:
    return _ph.check_needs_rehash(hashed)


# ---------- khóa dẫn xuất ----------
@lru_cache(maxsize=256)
def derive_key(purpose: str, context: str = "") -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=f"openguard:{purpose}:{context}".encode()).derive(settings.master_key_bytes())


def device_signing_key(device_id: str) -> bytes:
    return derive_key("policy-signing", device_id)


def encrypt_field(plaintext: str) -> str:
    nonce = secrets.token_bytes(12)
    ct = AESGCM(derive_key("field-enc")).encrypt(nonce, plaintext.encode(), b"ogk")
    return base64.urlsafe_b64encode(nonce + ct).decode()


def decrypt_field(token: str) -> str:
    raw = base64.urlsafe_b64decode(token.encode())
    return AESGCM(derive_key("field-enc")).decrypt(raw[:12], raw[12:], b"ogk").decode()


# ---------- ký chính sách ----------
def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sign_payload(payload: dict, key: bytes) -> str:
    return hmac.new(key, canonical_json(payload), hashlib.sha256).hexdigest()


def verify_payload(payload: dict, signature: str, key: bytes) -> bool:
    return isinstance(signature, str) and hmac.compare_digest(sign_payload(payload, key), signature)


# ---------- token ----------
def new_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_enroll_code() -> str:
    return "".join(secrets.choice(ENROLL_ALPHABET) for _ in range(settings.ENROLL_CODE_LENGTH))


def create_device_access_token(device_id: str, child_id: str) -> tuple[str, int]:
    ttl = settings.DEVICE_ACCESS_TTL_SECONDS
    now = datetime.now(timezone.utc)
    tok = jwt.encode({"sub": device_id, "cid": child_id, "typ": "device", "iat": now,
                      "exp": now + timedelta(seconds=ttl)}, derive_key("jwt"), algorithm="HS256")
    return tok, ttl


def decode_device_access_token(token: str) -> dict | None:
    try:
        data = jwt.decode(token, derive_key("jwt"), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return data if data.get("typ") == "device" else None


# ---------- TOTP (RFC 6238) ----------
def new_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _hotp(secret: str, counter: int) -> str:
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    h = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return f"{(struct.unpack('>I', h[o:o + 4])[0] & 0x7FFFFFFF) % 10**6:06d}"


def totp_now(secret: str, at: float | None = None) -> str:
    return _hotp(secret, int((at or time.time()) // 30))


def verify_totp(secret: str, code: str, last_counter: int = 0, at: float | None = None) -> int | None:
    """Trả về counter hợp lệ (chống dùng lại) hoặc None."""
    base = int((at or time.time()) // 30)
    for c in (base - 1, base, base + 1):
        if c > last_counter and hmac.compare_digest(_hotp(secret, c), code.strip()):
            return c
    return None
