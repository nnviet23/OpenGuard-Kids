"""Cấu hình pytest dùng chung: CSDL tạm, nạp server + agent vào sys.path."""
import os
import sys
import tempfile
from pathlib import Path

_tmp = tempfile.mkdtemp(prefix="ogk-test-")
os.environ["OGK_DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["OGK_MASTER_KEY"] = "test-master-key-0123456789-abcdefghijklmnop"
os.environ["OGK_SEED_DEMO"] = "false"
os.environ["OGK_ENV"] = "dev"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "openguard-server"))
sys.path.insert(0, str(ROOT / "openguard-agent" / "src"))

import warnings  # noqa: E402

warnings.filterwarnings("ignore")

import pytest  # noqa: E402


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.core.database import Base, engine
    from app.core.ratelimit import limiter
    from app.main import app

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    limiter.reset()
    with TestClient(app) as c:
        yield c


STRONG = "Mat-khau-Manh-2026"


def make_parent(client, email="a@example.com", password=STRONG):
    r = client.post("/api/v1/auth/register", json={"email": email, "password": password, "display_name": email})
    assert r.status_code == 201, r.text
    return login(client, email, password)


def login(client, email, password=STRONG):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    csrf = r.json()["csrf_token"]
    return {"X-CSRF-Token": csrf}


def make_child(client, h, name="Bé An"):
    r = client.post("/api/v1/children", json={"name": name, "age_group": "6-11"}, headers=h)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def enroll_device(client, h, child_id, name="PC"):
    r = client.post(f"/api/v1/children/{child_id}/enroll-code",
                    json={"parent_consent": True, "child_informed": True}, headers=h)
    assert r.status_code == 201, r.text
    code = r.json()["code"]
    e = client.post("/api/v1/agent/enroll", json={"code": code, "device_name": name, "fingerprint": "fp"})
    assert e.status_code == 200, e.text
    return e.json(), code
