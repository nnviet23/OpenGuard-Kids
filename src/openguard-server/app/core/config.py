"""Cấu hình server – đọc từ biến môi trường tiền tố OGK_ hoặc file .env."""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OGK_", env_file=".env", extra="ignore")

    ENV: str = "dev"  # dev | prod
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'ogk_server.db'}"
    MASTER_KEY: str = ""  # >= 32 ký tự; bắt buộc ở prod

    SESSION_COOKIE_NAME: str = "ogk_session"
    CSRF_COOKIE_NAME: str = "ogk_csrf"
    SESSION_TTL_SECONDS: int = 12 * 3600
    COOKIE_SECURE: bool = False  # đặt True khi chạy sau HTTPS (prod bắt buộc)

    PASSWORD_MIN_LENGTH: int = 10
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_LOCK_MINUTES: int = 15

    DEVICE_ACCESS_TTL_SECONDS: int = 15 * 60
    ENROLL_CODE_TTL_SECONDS: int = 10 * 60
    ENROLL_CODE_LENGTH: int = 8
    POLICY_VALID_DAYS: int = 7  # thời hạn chính sách cho chế độ offline
    HEARTBEAT_INTERVAL_SECONDS: int = 60
    OFFLINE_FAIL_MODE: str = "closed"  # fail-closed sau N ngày mất kết nối (xem PRIVACY/THREATMODEL)
    OFFLINE_FAIL_DAYS: int = 3

    RETENTION_DAYS: int = 90
    RETENTION_SWEEP_SECONDS: int = 6 * 3600

    RATE_LOGIN_PER_IP: int = 20  # / 5 phút
    RATE_GENERAL_PER_IP: int = 600  # / phút
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    TRUST_PROXY_HEADERS: bool = False

    SEED_DEMO: bool = True
    DEMO_EMAIL: str = "parent@example.com"
    DEMO_PASSWORD: str = "OpenGuard@2026"

    def master_key_bytes(self) -> bytes:
        if self.MASTER_KEY:
            if len(self.MASTER_KEY) < 32:
                raise RuntimeError("OGK_MASTER_KEY phải dài ít nhất 32 ký tự")
            return self.MASTER_KEY.encode()
        if self.ENV == "prod":
            raise RuntimeError("Môi trường prod bắt buộc đặt OGK_MASTER_KEY")
        path = BASE_DIR / "data" / ".dev_master_key"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(secrets.token_urlsafe(48))
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
        return path.read_text().strip().encode()


settings = Settings()
