
import time

from usage_tracker import UsageTracker, get_idle_seconds


def main() -> None:
    tracker = UsageTracker()

    print("OpenGuard usage tracker test")
    print("Move the mouse or press a key to remain active.")
    print("Leave the computer idle for more than 5 minutes to test idle detection.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            used_seconds = tracker.update()
            idle_seconds = get_idle_seconds()

            print(
                f"\rUsed: {used_seconds}s | "
                f"Idle: {int(idle_seconds)}s",
                end="",
                flush=True,
            )

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nTest stopped.")


if __name__ == "__main__":
    main()
