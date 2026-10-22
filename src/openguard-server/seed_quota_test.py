
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.parent import Parent
from app.models.device import Device
from app.models.device_policy import DevicePolicy

PARENT_ID = "par_e4a8b29c"
DEVICE_ID = "device_test_001"

db = SessionLocal()

try:
    parent = db.query(Parent).filter(Parent.id == PARENT_ID).first()

    if parent is None:
        parent = Parent(
            id=PARENT_ID,
            email="parent@openguard.com",
            hashed_password=hash_password("OpenGuard@2026"),
        )
        db.add(parent)

    device = db.query(Device).filter(Device.id == DEVICE_ID).first()

    if device is None:
        device = Device(
            id=DEVICE_ID,
            parent_id=PARENT_ID,
            name="Test Computer",
            policy_version=1,
        )
        db.add(device)

    db.flush()

    policy = (
        db.query(DevicePolicy)
        .filter(DevicePolicy.device_id == DEVICE_ID)
        .first()
    )

    if policy is None:
        policy = DevicePolicy(
            device_id=DEVICE_ID,
            weekday_limit_minutes=90,
            weekend_limit_minutes=120,
            enabled=True,
            version=1,
        )
        db.add(policy)

    db.commit()
    print("Test parent, device, and quota policy are ready.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
