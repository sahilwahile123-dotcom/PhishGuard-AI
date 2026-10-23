"""Lexical URL features. Strings only: the destination is NEVER contacted."""
import ipaddress, math, re
from urllib.parse import urlparse
from config import MAX_URL_LENGTH

SHORTENERS = {"bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly", "rebrand.ly", "cutt.ly", "shorturl.at"}
KEYWORDS = ("login", "verify", "update", "secure", "account", "bank", "confirm", "password", "signin", "paypal", "wallet")
FEATURE_NAMES = ["url_length", "host_length", "path_length", "query_length", "has_ip", "is_https",
                 "num_subdomains", "num_dots", "num_hyphens", "num_digits", "digit_ratio",
                 "num_special_chars", "has_at", "is_shortener", "unusual_port", "keyword_count", "host_entropy"]

def parse_url(raw):
    if not isinstance(raw, str):
        raise ValueError("URL must be text.")
    raw = raw.strip()
    if not raw:
        raise ValueError("URL is empty.")
    if len(raw) > MAX_URL_LENGTH:
        raise ValueError(f"URL is longer than {MAX_URL_LENGTH} characters.")
    if re.search(r"\s", raw):
        raise ValueError("URL must not contain spaces.")
    full = raw if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw) else "http://" + raw
    p = urlparse(full)
    if p.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs are supported.")
    try:
        p.port
    except ValueError:
        raise ValueError("URL has an invalid port.")
    host = p.hostname
    if not host or not re.fullmatch(r"[A-Za-z0-9.\-]+|[0-9a-fA-F:]+", host) or ".." in host:
        raise ValueError("URL has no valid host name.")
    return p

def _is_ip(host):
    try:
        ipaddress.ip_address(host); return True
    except ValueError:
        return False

def _entropy(s):
    return -sum((s.count(c) / len(s)) * math.log2(s.count(c) / len(s)) for c in set(s)) if s else 0.0

def extract_features(raw):
    p = parse_url(raw)
    url, host = raw.strip(), p.hostname
    ip = _is_ip(host)
    digits = sum(c.isdigit() for c in url)
    feats = {
        "url_length": len(url), "host_length": len(host), "path_length": len(p.path), "query_length": len(p.query),
        "has_ip": int(ip), "is_https": int(p.scheme == "https"),
        "num_subdomains": 0 if ip else max(len(host.split(".")) - 2, 0),
        "num_dots": url.count("."), "num_hyphens": url.count("-"), "num_digits": digits,
        "digit_ratio": round(digits / len(url), 4),
        "num_special_chars": sum(url.count(c) for c in "?=&%_~#$!*"),
        "has_at": int("@" in url), "is_shortener": int(host.lower().removeprefix("www.") in SHORTENERS),
        "unusual_port": int(p.port not in (None, 80, 443)),
        "keyword_count": sum(k in url.lower() for k in KEYWORDS), "host_entropy": round(_entropy(host), 4),
    }
    return {k: feats[k] for k in FEATURE_NAMES}  # fixed order for training and prediction
