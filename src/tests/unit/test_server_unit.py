"""Kiểm thử đơn vị phía server (không cần HTTP)."""
import base64
import time
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app import classification as cls
from app.core import security as sec
from app.core.ratelimit import SlidingWindowLimiter


def test_password_policy_rejects_short_and_weak():
    assert sec.validate_password("Ab1")  # quá ngắn
    assert sec.validate_password("alllowercase1234")  # thiếu chữ hoa
    assert sec.validate_password("Mat-khau-Manh-2026") == []


def test_argon2id_hash_and_verify():
    h = sec.hash_password("Mat-khau-Manh-2026")
    assert h.startswith("$argon2id$")
    assert sec.verify_password("Mat-khau-Manh-2026", h)
    assert not sec.verify_password("sai-mat-khau-123A", h)
    assert not sec.verify_password("x", None)  # user không tồn tại vẫn an toàn


def test_field_encryption_roundtrip_and_tamper():
    token = sec.encrypt_field("bí mật")
    assert sec.decrypt_field(token) == "bí mật"
    raw = bytearray(base64.urlsafe_b64decode(token))
    raw[-1] ^= 1
    with pytest.raises(Exception):
        sec.decrypt_field(base64.urlsafe_b64encode(bytes(raw)).decode())


def test_policy_signature_detects_tampering():
    key = sec.device_signing_key("dev1")
    payload = {"a": 1, "limit": 60, "s": [True, False]}
    sig = sec.sign_payload(payload, key)
    assert sec.verify_payload(payload, sig, key)
    assert not sec.verify_payload({**payload, "limit": 600}, sig, key)
    assert not sec.verify_payload(payload, sig, sec.device_signing_key("dev2"))  # khóa theo thiết bị


def test_totp_rfc6238_vector():
    secret = base64.b32encode(b"12345678901234567890").decode()
    assert sec.totp_now(secret, at=59) == "287082"  # RFC 6238, T=59, 6 chữ số


def test_totp_replay_rejected():
    s = sec.new_totp_secret()
    code = sec.totp_now(s)
    c = sec.verify_totp(s, code, 0)
    assert c is not None
    assert sec.verify_totp(s, code, c) is None  # không dùng lại được


def test_device_token_roundtrip_and_expiry():
    tok, ttl = sec.create_device_access_token("d1", "c1")
    assert ttl == 900  # 15 phút
    assert sec.decode_device_access_token(tok)["sub"] == "d1"
    expired = jwt.encode({"sub": "d1", "typ": "device", "exp": datetime.now(timezone.utc) - timedelta(seconds=5)},
                         sec.derive_key("jwt"), algorithm="HS256")
    assert sec.decode_device_access_token(expired) is None
    assert sec.decode_device_access_token("rác") is None


def test_enroll_code_format():
    for _ in range(50):
        c = sec.new_enroll_code()
        assert len(c) == 8 and all(ch in sec.ENROLL_ALPHABET for ch in c)


def test_classification_table_size_and_categories():
    t = cls.load_table()
    assert len(t) >= 200
    assert set(t.values()) == set(cls.CATEGORIES)  # đủ 6 nhóm


def test_classify_matches_subdomains():
    assert cls.classify("vi.m.wikipedia.org") == "education"
    assert cls.classify("khong-co-trong-bang.xyz") == "uncategorized"


def test_default_policy_6_11():
    act, cat, why = cls.decide_domain("www.facebook.com", {}, {})
    assert (act, cat) == ("block", "social") and why == "category:social"
    assert cls.decide_domain("khanacademy.org", {}, {})[0] == "allow"


def test_override_beats_category_but_whitelist_beats_all():
    assert cls.decide_domain("roblox.com", {}, {"roblox.com": "allow"})[0] == "allow"
    assert cls.decide_domain("truong.edu.vn", {}, {"truong.edu.vn": "block"})[0] == "allow"  # NT6
    assert cls.decide_domain("tongdai111.vn", {"education": "block"}, {})[2] == "safety_whitelist"


def test_event_validation_rejects_urls_and_paths():
    from app.routers.agent import EventIn, _validate_event
    now = datetime.now(timezone.utc)

    def ev(type_, subject):
        return EventIn(event_id="abcdefgh1", ts=now, type=type_, subject=subject)

    assert _validate_event(ev("domain_query", "khanacademy.org")) is None
    assert _validate_event(ev("domain_query", "https://khanacademy.org/x?q=1")) is not None
    assert _validate_event(ev("domain_query", "khanacademy.org/path")) is not None
    assert _validate_event(ev("app_stop", "C:\\Users\\x\\a.exe")) is not None
    assert _validate_event(ev("khong_hop_le", "a")) is not None
    old = EventIn(event_id="abcdefgh2", ts=now - timedelta(days=200), type="app_start", subject="a.exe")
    assert _validate_event(old) is not None


def test_audit_chain_detects_tampering(client):
    from app.core.audit import verify_chain, write_audit
    from app.core.database import SessionLocal
    from app.models import AuditLog
    with SessionLocal() as db:
        for i in range(3):
            write_audit(db, "x", actor_type="system", new={"i": i})
        db.commit()
        assert verify_chain(db) == (True, None)
        row = db.get(AuditLog, 2)
        row.new_value = '{"i": 99}'
        db.commit()
        ok, bad = verify_chain(db)
        assert not ok and bad == 2


def test_sliding_window_limiter():
    l = SlidingWindowLimiter()
    assert all(l.allow("k", 3, 60) for _ in range(3))
    assert not l.allow("k", 3, 60)
    assert l.allow("other", 3, 60)


def test_utc_datetime_roundtrip(client):
    from app.core.database import SessionLocal, utcnow
    from app.models import Account
    with SessionLocal() as db:
        a = Account(email="t@example.com", password_hash="x", role="parent", locked_until=utcnow())
        db.add(a)
        db.commit()
        db.expire_all()
        assert db.get(Account, a.id).locked_until.tzinfo is not None


def test_dataset_50_domains_classified_as_expected():
    from pathlib import Path
    lines = [l.split() for l in (Path(__file__).parents[1] / "datasets" / "test_domains_50.txt").read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    assert len(lines) == 50
    wrong = [(d, want, cls.classify(d)) for d, want in lines if cls.classify(d) != want]
    assert wrong == []
