from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.features.auth.router import router as auth_router
from app.features.devices.router import router as agent_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend API điều phối hệ thống OpenGuard Kids"
)

# Cấu hình CORS để cho phép Frontend gửi Cookie (allow_credentials=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nạp các router tính năng
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(agent_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": "/docs"
    }
