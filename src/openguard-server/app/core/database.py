
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


DATABASE_URL = settings.DATABASE_URL

# Tạo thư mục chứa database nếu chưa tồn tại.
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.removeprefix("sqlite:///")

    if db_path != ":memory:":
        path = Path(db_path)

        if not path.is_absolute():
            path = Path.cwd() / path

        path.parent.mkdir(parents=True, exist_ok=True)

        # Dùng đường dẫn tuyệt đối để kết nối ổn định.
        DATABASE_URL = f"sqlite:///{path.resolve().as_posix()}"

# Tạo engine kết nối database.
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite:")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

# Tạo session để truy vấn database.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Lớp gốc cho các model SQLAlchemy.
class Base(DeclarativeBase):
    pass


# Cung cấp session cho các API.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
