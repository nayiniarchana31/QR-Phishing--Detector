import math
import re
from collections import Counter
from urllib.parse import urlparse

FEATURE_NAMES = [
    "url_length",
    "domain_length",
    "num_dots",
    "num_hyphens",
    "num_at_signs",
    "num_percent",
    "num_question_marks",
    "num_equals",
    "num_underscores",
    "num_slashes",
    "has_ip_address",
    "is_https",
    "num_subdomains",
    "has_suspicious_words",
    "url_entropy",
    "has_port",
    "digit_ratio",
    "double_slash_redirect",
    "hostname_length",
    "path_length",
]

SUSPICIOUS_WORDS = {
    "login", "signin", "account", "update", "secure", "banking",
    "verify", "confirm", "paypal", "password", "credential", "alert",
    "suspended", "limited", "unusual", "activity", "free", "winner",
    "prize", "urgent", "support", "admin", "ebay", "amazon",
}

_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0

    counts = Counter(value)
    length = len(value)
    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )
    return round(entropy, 4)


def extract_features(url: str) -> dict:
    """Extract the 20 URL features described in the project report."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    url_lower = url.lower()

    try:
        has_port = int(parsed.port is not None)
    except ValueError:
        has_port = 0

    return {
        "url_length": len(url),
        "domain_length": len(hostname),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_at_signs": url.count("@"),
        "num_percent": url.count("%"),
        "num_question_marks": url.count("?"),
        "num_equals": url.count("="),
        "num_underscores": url.count("_"),
        "num_slashes": url.count("/"),
        "has_ip_address": int(bool(_IP_RE.match(hostname))),
        "is_https": int(parsed.scheme.lower() == "https"),
        "num_subdomains": max(0, len(hostname.split(".")) - 2) if hostname else 0,
        "has_suspicious_words": int(
            any(word in url_lower for word in SUSPICIOUS_WORDS)
        ),
        "url_entropy": _shannon_entropy(url),
        "has_port": has_port,
        "digit_ratio": (
            round(sum(char.isdigit() for char in url) / len(url), 4)
            if url else 0.0
        ),
        "double_slash_redirect": int("//" in path),
        "hostname_length": len(hostname),
        "path_length": len(path),
    }


def features_to_vector(features: dict) -> list:
    """Return features in the exact order expected by the model."""
    return [features[name] for name in FEATURE_NAMES]
