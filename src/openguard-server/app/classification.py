"""Phân loại tên miền (6 nhóm), chính sách mặc định cho trẻ 6–11 và danh sách an toàn NT6."""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

CATEGORIES = ["education", "entertainment", "social", "games", "inappropriate", "uncategorized"]
CATEGORY_LABELS_VI = {"education": "Giáo dục", "entertainment": "Giải trí", "social": "Mạng xã hội",
                      "games": "Trò chơi", "inappropriate": "Không phù hợp lứa tuổi", "uncategorized": "Chưa phân loại"}
ACTIONS = {"allow", "limit", "block", "log"}

# Chính sách mặc định cho trẻ 6–11 tuổi (phụ huynh có thể đổi từng nhóm)
DEFAULT_ACTIONS_6_11 = {
    "education": "allow",
    "entertainment": "limit",   # tính vào ngân sách thời gian
    "social": "block",
    "games": "limit",
    "inappropriate": "block",
    "uncategorized": "log",     # cho phép nhưng ghi nhận để phụ huynh xem
}

# NT6 – danh sách an toàn vĩnh viễn: KHÔNG bao giờ bị chặn, kể cả khi hết giờ
# (cổng trường học, tổng đài 111, dịch vụ khẩn cấp). Mã nguồn cố định, không sửa qua API.
SAFETY_WHITELIST = ["edu.vn", "gov.vn", "tongdai111.vn", "vnedu.vn", "classroom.google.com"]

# Tên miền SafeSearch: ép sang CNAME công bố chính thức của Google/Bing/YouTube
SAFESEARCH_CNAME = {
    "www.google.com": "forcesafesearch.google.com",
    "google.com": "forcesafesearch.google.com",
    "www.google.com.vn": "forcesafesearch.google.com",
    "www.bing.com": "strict.bing.com",
    "www.youtube.com": "restrict.youtube.com",
    "m.youtube.com": "restrict.youtube.com",
    "youtube.com": "restrict.youtube.com",
    "duckduckgo.com": "safe.duckduckgo.com",
}

# Dịch vụ DoH phổ biến – agent chặn để tránh vượt qua DNS proxy
DOH_PROVIDERS = ["dns.google", "cloudflare-dns.com", "mozilla.cloudflare-dns.com", "dns.quad9.net",
                 "doh.opendns.com", "dns.nextdns.io", "doh.cleanbrowsing.org"]


@lru_cache(maxsize=1)
def load_table() -> dict[str, str]:
    path = Path(__file__).parent / "data" / "classification.csv"
    with path.open(encoding="utf-8") as f:
        return {r["domain"].strip().lower(): r["category"] for r in csv.DictReader(f)}


def _suffixes(domain: str):
    parts = domain.strip(".").lower().split(".")
    for i in range(len(parts) - 1):
        yield ".".join(parts[i:])


def is_whitelisted(domain: str) -> bool:
    return any(s in SAFETY_WHITELIST for s in _suffixes(domain)) or domain.lower().strip(".") in SAFETY_WHITELIST


def classify(domain: str, table: dict[str, str] | None = None) -> str:
    table = table if table is not None else load_table()
    for s in _suffixes(domain):
        if s in table:
            return table[s]
    return "uncategorized"


def decide_domain(domain: str, category_actions: dict[str, str], overrides: dict[str, str],
                  table: dict[str, str] | None = None) -> tuple[str, str, str]:
    """Trả (action, category, lý do/nguồn quy tắc). Ưu tiên: whitelist > override > nhóm."""
    if is_whitelisted(domain):
        return "allow", "education", "safety_whitelist"
    for s in _suffixes(domain):
        if s in overrides:
            return overrides[s], classify(domain, table), f"override:{s}"
    cat = classify(domain, table)
    action = {**DEFAULT_ACTIONS_6_11, **(category_actions or {})}.get(cat, "log")
    return action, cat, f"category:{cat}"
