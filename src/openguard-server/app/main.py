from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import classification as cls
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.ratelimit import general_rate_limit
from app.retention import retention_loop
from app.routers import agent, auth, children, devices, privacy, reports, requests as requests_router

log = logging.getLogger("ogk")
WEB_DIST = Path(__file__).resolve().parents[2] / "openguard-web" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.master_key_bytes()  # fail sớm nếu prod thiếu khóa
    Base.metadata.create_all(engine)
    if settings.SEED_DEMO and settings.ENV != "prod":
        from app.seed import seed_demo
        with SessionLocal() as db:
            if seed_demo(db):
                log.warning("Đã nạp dữ liệu mẫu: %s / %s", settings.DEMO_EMAIL, settings.DEMO_PASSWORD)
    task = asyncio.create_task(retention_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="OpenGuard Kids Server", version="1.0.0", lifespan=lifespan,
              docs_url=None if settings.ENV == "prod" else "/docs", redoc_url=None, openapi_url=None if settings.ENV == "prod" else "/openapi.json")

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True,
                   allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type", "X-CSRF-Token", "Authorization"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    resp.headers.setdefault("Content-Security-Policy",
                            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'")
    if request.url.path.startswith("/api"):
        resp.headers["Cache-Control"] = "no-store"
    if request.url.scheme == "https" or settings.ENV == "prod":
        resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
    return resp


API = "/api/v1"
for r in (auth.router, children.router, devices.router, agent.router, requests_router.router,
          reports.router, privacy.router):
    app.include_router(r, prefix=API, dependencies=[Depends(general_rate_limit)] if r is not agent.router else [])


@app.get(f"{API}/health")
def health():
    return {"status": "ok"}


@app.get(f"{API}/meta/categories")
def categories():
    return {"categories": [{"id": c, "label": cls.CATEGORY_LABELS_VI[c]} for c in cls.CATEGORIES],
            "default_actions_6_11": cls.DEFAULT_ACTIONS_6_11, "actions": sorted(cls.ACTIONS),
            "safety_whitelist": cls.SAFETY_WHITELIST, "table_size": len(cls.load_table())}


@app.get(f"{API}/meta/classify")
def classify_domain(domain: str):
    d = domain.strip().lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    if not d or len(d) > 253:
        return JSONResponse({"detail": "Tên miền không hợp lệ"}, status_code=422)
    return {"domain": d, "category": cls.classify(d), "whitelisted": cls.is_whitelisted(d)}


if WEB_DIST.exists():  # phục vụ dashboard đã build => 1 tiến trình, 1 cổng
    app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        f = (WEB_DIST / full_path).resolve()
        if full_path and f.is_file() and WEB_DIST in f.parents:
            return FileResponse(f)
        return FileResponse(WEB_DIST / "index.html")
