import socket
import threading
import dns.message
import dns.rcode
import dns.query
from typing import Set


UPSTREAM_DNS = "1.1.1.1" 
UPSTREAM_PORT = 53
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 53


class DnsProxyServer:
    def __init__(self, blocked_domains: Set[str] = None):
        self.blocked_domains = {d.lower().strip(".") for d in (blocked_domains or {
            "roblox.com",
            "discord.com",
            "tiktok.com",
        })}


        self.exempt_domains = {
            "tongdai111.vn",
            "baovechamsocsolieu.gov.vn",
            "khanacademy.org",
            "scratch.mit.edu",
        }

        self.doh_canary_domains = {
            "use-application-dns.net",
        }

        self._running = False
        self._sock = None

    def _is_blocked(self, qname: str) -> bool:
        domain = qname.lower().strip(".")

        for exempt in self.exempt_domains:
            if domain == exempt or domain.endswith("." + exempt):
                return False

        for canary in self.doh_canary_domains:
            if domain == canary or domain.endswith("." + canary):
                return True

        for blocked in self.blocked_domains:
            if domain == blocked or domain.endswith("." + blocked):
                return True

        return False

    def _handle_query(self, data: bytes, client_addr: tuple):
        try:
            req = dns.message.from_wire(data)
            if not req.question:
                return

            qname = str(req.question[0].name)

            if self._is_blocked(qname):

                resp = dns.message.make_response(req)
                resp.set_rcode(dns.rcode.NXDOMAIN)
                self._sock.sendto(resp.to_wire(), client_addr)
                print(f"[DNS PROXY] BLOCKED: {qname.strip('.')} -> NXDOMAIN")
            else:
                # Chuyển tiếp truy vấn hợp lệ lên DNS Upstream
                upstream_resp = dns.query.udp(req, UPSTREAM_DNS, port=UPSTREAM_PORT, timeout=2.5)
                self._sock.sendto(upstream_resp.to_wire(), client_addr)

        except Exception as e:
            pass

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self._sock.bind((LISTEN_HOST, LISTEN_PORT))
        except PermissionError:
            print("[DNS PROXY] LỖI: Cần quyền Administrator/SYSTEM để bind cổng 53!")
            return

        self._running = True
        print(f"[DNS PROXY] Đang lắng nghe tại {LISTEN_HOST}:{LISTEN_PORT}")

        while self._running:
            try:
                data, addr = self._sock.recvfrom(4096)
                threading.Thread(
                    target=self._handle_query,
                    args=(data, addr),
                    daemon=True
                ).start()
            except OSError:
                break

    def stop(self):
        self._running = False
        if self._sock:
            self._sock.close()