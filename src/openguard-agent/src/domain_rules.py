"""Quyết định cho một tên miền theo chính sách (bản agent của app/classification.py)."""
from __future__ import annotations


def normalize(domain: str) -> str:
    return domain.strip().strip(".").lower()


def suffixes(domain: str):
    parts = normalize(domain).split(".")
    for i in range(len(parts) - 1):
        yield ".".join(parts[i:])


def is_whitelisted(domain: str, whitelist: list[str]) -> bool:
    wl = set(whitelist)
    return any(s in wl for s in suffixes(domain)) or normalize(domain) in wl


def classify(domain: str, table: dict[str, str]) -> str:
    for s in suffixes(domain):
        if s in table:
            return table[s]
    return "uncategorized"


def decide(domain: str, policy: dict) -> tuple[str, str, str]:
    """Trả (action, category, reason). Ưu tiên: danh sách an toàn > override > nhóm."""
    domain = normalize(domain)
    if is_whitelisted(domain, policy.get("safety_whitelist", [])):
        return "allow", "education", "safety_whitelist"
    cat = classify(domain, policy.get("domain_categories", {}))
    overrides = policy.get("domain_overrides", {})
    for s in suffixes(domain):
        if s in overrides:
            return overrides[s], cat, f"override:{s}"
    action = policy.get("category_actions", {}).get(cat, "log")
    return action, cat, f"category:{cat}"
