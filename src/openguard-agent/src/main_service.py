"""OpenGuard Kids – agent (dòng lệnh + dịch vụ Windows).

    python main_service.py enroll --code ABCD2345 [--server https://host:8443/api/v1] [--name "Máy phòng khách"]
    python main_service.py run          # chạy ở console (dev) – thoát bằng Ctrl+C
    python main_service.py status
    python main_service.py unenroll     # gỡ ghép cặp hợp lệ, khôi phục DNS, xóa dữ liệu cục bộ (KHÔNG có chống gỡ)
    python main_service.py service install|start|stop|remove      (Windows, quyền Administrator)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import platform
import sys
import threading
import uuid

from agent_core import AGENT_VERSION, AgentConfig, AgentCore
from api_client import ApiClient, ApiError
from offline_store import OfflineStore

log = logging.getLogger("og")


def build_core(cfg: AgentConfig, http=None) -> AgentCore:
    from pathlib import Path
    store = OfflineStore(Path(cfg.data_dir) / "agent.db")
    api = ApiClient(cfg.server_url, store, http=http, pin_sha256=cfg.pin_sha256, ca_file=cfg.ca_file)
    from usage_tracker import UsageTracker
    from app_control import AppController
    dns_guard = None
    if cfg.manage_dns:
        from dns_config import DnsGuard
        dns_guard = DnsGuard()
    return AgentCore(cfg, store, api, UsageTracker(), apps=AppController(enforce=cfg.enforce_apps), dns_guard=dns_guard)


def start_background(core: AgentCore, cfg: AgentConfig, stop: threading.Event) -> list:
    """DNS proxy, IPC cho khay, WebSocket lệnh khẩn."""
    from dns_proxy import DnsFilter, DnsProxyServer, udp_upstream
    from ipc import IpcServer
    from ws_client import run_ws
    servers = []
    ipc = IpcServer(core, cfg.data_dir)
    ipc.start()
    servers.append(ipc)
    if cfg.manage_dns:
        try:
            flt = DnsFilter(lambda: core.policy, udp_upstream(cfg.upstream_dns), core.on_dns_event, core.group_exceeded)
            dns_srv = DnsProxyServer(flt, "127.0.0.1", cfg.dns_port)
            dns_srv.start()
            servers.append(dns_srv)
            if core.dns_guard and cfg.dns_port == 53:
                core.dns_guard.apply()
        except OSError as e:
            log.error("Không mở được DNS proxy cổng %s (%s) – cần quyền Administrator", cfg.dns_port, e)
            core.notifier.push("Bộ lọc DNS chưa hoạt động", "Dịch vụ cần quyền cao hơn để mở cổng DNS.", "warn")
    threading.Thread(target=run_ws, args=(core, stop), daemon=True, name="og-ws").start()
    return servers


def cmd_enroll(args, cfg: AgentConfig) -> int:
    core = build_core(cfg)
    fp = hashlib.sha256(f"{platform.node()}-{uuid.getnode()}".encode()).hexdigest()
    try:
        d = core.api.enroll(args.code, args.name or platform.node() or "Máy tính", fp, AGENT_VERSION)
    except ApiError as e:
        print(f"Ghép cặp thất bại: {e.detail}")
        return 1
    print(f"Đã ghép cặp thiết bị {d['device_id']} (mã chỉ dùng một lần, hiệu lực 10 phút).")
    print("Phụ huynh đã đồng ý khi tạo mã; hãy chắc chắn trẻ đã được thông báo về việc này.")
    return 0


def cmd_run(cfg: AgentConfig) -> int:
    core = build_core(cfg)
    if not core.api.creds:
        print("Chưa ghép cặp. Chạy: python main_service.py enroll --code <MÃ 8 KÝ TỰ>")
        return 1
    stop = threading.Event()
    servers = start_background(core, cfg, stop)
    print(f"OpenGuard Kids đang chạy. enforce_lock={cfg.enforce_lock} enforce_apps={cfg.enforce_apps} dns={cfg.manage_dns}")
    try:
        core.run_forever(stop)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        for s in servers:
            try:
                getattr(s, "stop", getattr(s, "shutdown", lambda: None))()
            except Exception:
                pass
    return 0


def cmd_status(cfg: AgentConfig) -> int:
    core = build_core(cfg)
    c = core.api.creds
    print(json.dumps({"enrolled": bool(c), "device_id": (c or {}).get("device_id"), "pending_events": core.store.pending_count(),
                      "last_contact": core.store.get("last_contact"), "server": cfg.server_url}, ensure_ascii=False, indent=2))
    return 0


def cmd_unenroll(cfg: AgentConfig) -> int:
    core = build_core(cfg)
    if core.api.creds:
        try:
            core.flush_events()
            core.api.uninstall_notice("user_requested")
        except Exception:
            pass
    core._handle_revoked()
    print("Đã gỡ ghép cặp, khôi phục DNS và xóa dữ liệu cục bộ.")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser(prog="openguard-agent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enroll")
    e.add_argument("--code", required=True)
    e.add_argument("--server")
    e.add_argument("--name")
    sub.add_parser("run")
    sub.add_parser("status")
    sub.add_parser("unenroll")
    s = sub.add_parser("service")
    s.add_argument("action", choices=["install", "start", "stop", "remove"])
    args = ap.parse_args(argv)
    cfg = AgentConfig.from_env()
    if getattr(args, "server", None):
        cfg.server_url = args.server
    if args.cmd == "enroll":
        return cmd_enroll(args, cfg)
    if args.cmd == "run":
        return cmd_run(cfg)
    if args.cmd == "status":
        return cmd_status(cfg)
    if args.cmd == "unenroll":
        return cmd_unenroll(cfg)
    if args.cmd == "service":
        import windows_service
        return windows_service.handle(args.action)
    return 2


if __name__ == "__main__":
    sys.exit(main())
