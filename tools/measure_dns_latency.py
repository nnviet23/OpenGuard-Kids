"""Đo độ trễ truy vấn DNS (M4): so sánh DNS thượng nguồn trực tiếp với DNS proxy của OpenGuard.

    python measure_dns_latency.py --proxy 127.0.0.1:53 --upstream 8.8.8.8:53 --n 50 --out dns_latency.csv

Mỗi tên miền được hỏi ở cả hai đích, xen kẽ, để cùng điều kiện mạng. Ghi CSV từng mẫu và in
min/mean/median/p95/max (ms). Cần >= 30 mẫu theo đề bài. Tên miền dùng danh sách trung lập.
"""
import argparse
import csv
import statistics as st
import time

import dns.exception
import dns.message
import dns.query

DOMAINS = ["khanacademy.org", "vi.wikipedia.org", "coursera.org", "duolingo.com", "scratch.mit.edu", "code.org",
           "hocmai.vn", "olm.vn", "britannica.com", "ted.com", "nasa.gov", "w3schools.com", "quizlet.com", "openstax.org",
           "mathsisfun.com", "example.com", "github.com", "python.org", "mozilla.org", "iana.org"]


def ask(server: str, name: str, timeout: float = 3.0):
    host, _, port = server.partition(":")
    q = dns.message.make_query(name, "A")
    t0 = time.perf_counter()
    try:
        r = dns.query.udp(q, host, port=int(port or 53), timeout=timeout)
        return (time.perf_counter() - t0) * 1000, r.rcode()
    except dns.exception.Timeout:
        return None, "timeout"


def summarize(label: str, xs: list[float]) -> None:
    if not xs:
        print(f"{label}: không có mẫu hợp lệ")
        return
    xs = sorted(xs)
    p95 = xs[min(len(xs) - 1, int(round(0.95 * (len(xs) - 1))))]
    print(f"{label:10s} n={len(xs):3d} min={xs[0]:.1f} mean={st.mean(xs):.1f} median={st.median(xs):.1f} p95={p95:.1f} max={xs[-1]:.1f} (ms)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proxy", default="127.0.0.1:53")
    ap.add_argument("--upstream", default="8.8.8.8:53")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--out", default="dns_latency.csv")
    a = ap.parse_args()
    rows, direct, proxy = [], [], []
    for i in range(a.n):
        name = DOMAINS[i % len(DOMAINS)]
        for label, srv, bucket in (("upstream", a.upstream, direct), ("proxy", a.proxy, proxy)):
            ms, rc = ask(srv, name)
            rows.append([i, name, label, f"{ms:.2f}" if ms is not None else "", rc])
            if ms is not None:
                bucket.append(ms)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["sample", "domain", "target", "latency_ms", "rcode"], *rows])
    summarize("upstream", direct)
    summarize("proxy", proxy)
    if direct and proxy:
        print(f"Chênh lệch trung vị proxy - upstream: {st.median(proxy) - st.median(direct):+.1f} ms")
    print(f"Đã ghi {a.out}. Lưu ý: lần đầu có thể chậm do bộ nhớ đệm DNS lạnh – nên chạy 2 lượt và nêu rõ trong báo cáo.")


if __name__ == "__main__":
    main()
