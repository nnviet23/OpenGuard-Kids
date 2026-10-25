"""Xác minh chữ ký HMAC-SHA256 của gói chính sách do server cấp.

Khóa là khóa riêng của THIẾT BỊ (dẫn xuất từ master key bằng HKDF phía server, trao cho agent
một lần lúc ghép cặp qua TLS), nên một máy bị xâm phạm không giả mạo được chính sách của máy khác.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_policy_signature(payload: dict[str, Any], signature: str | None, key: bytes | str | None) -> bool:
    if not isinstance(signature, str) or not signature or not key or not isinstance(payload, dict):
        return False
    secret = key.encode("utf-8") if isinstance(key, str) else key
    expected = hmac.new(secret, canonical_json(payload), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_bundle(bundle: dict[str, Any] | None, key: bytes | str | None, expected_device_id: str | None = None) -> bool:
    """bundle = {"policy": {...}, "signature": "..."}; chống dùng nhầm gói của thiết bị khác."""
    if not isinstance(bundle, dict):
        return False
    policy = bundle.get("policy")
    if not isinstance(policy, dict) or not verify_policy_signature(policy, bundle.get("signature"), key):
        return False
    return expected_device_id is None or policy.get("device_id") == expected_device_id
