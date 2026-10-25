"""DNS proxy cục bộ 127.0.0.1:53 – lọc tên miền theo chính sách (F2).

* Chặn cả tên miền con (so khớp hậu tố). Danh sách an toàn NT6 không bao giờ bị chặn.
* SafeSearch bằng DNS: trả CNAME tới forcesafesearch.google.com / strict.bing.com / restrict.youtube.com.
* Đối phó DoH: các nhà cung cấp DoH phổ biến và tên miền canary của Firefox bị trả NXDOMAIN
  để trình duyệt quay về DNS hệ thống (đi qua proxy này).
* Chỉ ghi tên miền (không URL), tối đa một sự kiện/tên miền/30 giây.
"""
from __future__ import annotations

import logging
import socket
import socketserver
import threading
import time
from typing import Callable

import dns.flags
import dns.message
import dns.name
import dns.query
import dns.rcode
import dns.rdataclass
import dns.rdatatype
import dns.rrset

from domain_rules import decide, is_whitelisted, normalize, suffixes

log = logging.getLogger("og.dns")
DOH_CANARY = {"use-application-dns.net"}
DEDUP_SECONDS = 30


class DnsFilter:
    def __init__(self, get_policy: Callable[[], dict | None], upstream: Callable[[bytes], bytes],
                 on_event: Callable[[str, str, str], None] | None = None,
                 group_exceeded: Callable[[str], bool] | None = None, mono=time.monotonic) -> None:
        self.get_policy, self.upstream = get_policy, upstream
        self.on_event = on_event or (lambda *_: None)
        self.group_exceeded = group_exceeded or (lambda _g: False)
        self._mono, self._seen = mono, {}

    def _emit(self, kind: str, domain: str, policy_id: str) -> None:
        key = (kind, domain)
        now = self._mono()
        if now - self._seen.get(key, -1e9) < DEDUP_SECONDS:
            return
        self._seen[key] = now
        if len(self._seen) > 5000:
            self._seen = {k: v for k, v in self._seen.items() if now - v < DEDUP_SECONDS}
        self.on_event(kind, domain, policy_id)

    def handle(self, wire: bytes) -> bytes:
        try:
            query = dns.message.from_wire(wire)
        except Exception:
            return b""
        if not query.question:
            return self._rcode(query, dns.rcode.FORMERR)
        q = query.question[0]
        name = normalize(q.name.to_text())
        policy = self.get_policy()
        if not policy or not policy.get("enabled", True):
            return self._forward(wire, query)
        pid = policy.get("policy_id", "v0")
        whitelisted = is_whitelisted(name, policy.get("safety_whitelist", []))

        if not whitelisted and (name in DOH_CANARY or any(s in set(policy.get("doh_providers", [])) for s in suffixes(name))):
            self._emit("blocked_domain", name, f"{pid}:override:doh")
            return self._rcode(query, dns.rcode.NXDOMAIN)

        action, cat, reason = decide(name, policy)
        if action == "limit" and self.group_exceeded(cat):
            action, reason = "block", f"group_budget:{cat}"
        if action == "block":
            self._emit("blocked_domain", name, f"{pid}:{reason}")
            return self._rcode(query, dns.rcode.NXDOMAIN)

        self._emit("domain_query", name, f"{pid}:{reason}")
        target = (policy.get("safesearch_map") or {}).get(name)
        if target and q.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA, dns.rdatatype.CNAME):
            resp = self._safesearch(query, q, target)
            if resp is not None:
                return resp
        return self._forward(wire, query)

    # ---- helpers ----
    def _rcode(self, query: dns.message.Message, rc: int) -> bytes:
        r = dns.message.make_response(query)
        r.set_rcode(rc)
        return r.to_wire()

    def _forward(self, wire: bytes, query: dns.message.Message) -> bytes:
        try:
            return self.upstream(wire)
        except Exception:
            log.warning("upstream DNS lỗi")
            return self._rcode(query, dns.rcode.SERVFAIL)

    def _safesearch(self, query, q, target: str) -> bytes | None:
        try:
            sub = dns.message.make_query(target, q.rdtype if q.rdtype != dns.rdatatype.CNAME else dns.rdatatype.A)
            up = dns.message.from_wire(self.upstream(sub.to_wire()))
        except Exception:
            return None
        resp = dns.message.make_response(query)
        resp.flags |= dns.flags.RA
        resp.answer.append(dns.rrset.from_text(q.name, 300, "IN", "CNAME", target + "."))
        for rrset in up.answer:
            if rrset.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA):
                resp.answer.append(dns.rrset.from_rdata_list(dns.name.from_text(target), 300, list(rrset)))
        return resp.to_wire()


def udp_upstream(server: str, timeout: float = 3.0) -> Callable[[bytes], bytes]:
    def forward(wire: bytes) -> bytes:
        msg = dns.message.from_wire(wire)
        resp = dns.query.udp(msg, server, timeout=timeout)
        if resp.flags & dns.flags.TC:  # bị cắt -> thử lại bằng TCP
            resp = dns.query.tcp(msg, server, timeout=timeout)
        return resp.to_wire()
    return forward


class _Handler(socketserver.BaseRequestHandler):
    def handle(self):
        data, sock = self.request
        out = self.server.filter.handle(data)  # type: ignore[attr-defined]
        if out:
            sock.sendto(out, self.client_address)


class DnsProxyServer(socketserver.ThreadingUDPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, flt: DnsFilter, host: str = "127.0.0.1", port: int = 53) -> None:
        self.filter = flt
        super().__init__((host, port), _Handler)

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self.serve_forever, daemon=True, name="og-dns")
        t.start()
        return t
