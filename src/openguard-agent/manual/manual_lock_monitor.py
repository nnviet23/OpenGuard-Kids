
import time
from lock_monitor import LockMonitor

monitor = LockMonitor()
monitor.start()

print("Lock monitor started.")
print("Press Ctrl+C to stop.")

try:
    while True:
        print(f"Locked: {monitor.is_locked}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Test stopped.")
