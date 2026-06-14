"""Target input validation for the Target Management phase.

This module intentionally performs validation only. It does not execute scans,
external tools, shell commands, or network operations.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse, urlunparse

_ALLOWED_URL_SCHEMES = {"http", "https"}
_DANGEROUS_CHARACTERS = (";", "&", "|", "$", "`", ">", "<", "\n", "\r")
_DOMAIN_LABEL_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def _has_dangerous_characters(value: str) -> bool:
    return any(character in value for character in _DANGEROUS_CHARACTERS)


def _looks_like_range(value: str) -> bool:
    if "-" not in value:
        return False

    start, _, end = value.partition("-")
    start = start.strip()
    end = end.strip()
    if not start or not end:
        return False

    try:
        ipaddress.IPv4Address(start)
        ipaddress.IPv4Address(end)
        return True
    except ValueError:
        return False


def _is_valid_domain(value: str) -> bool:
    if len(value) > 253 or value.endswith("."):
        return False

    labels = value.split(".")
    if len(labels) < 2:
        return False

    if not all(_DOMAIN_LABEL_RE.fullmatch(label) for label in labels):
        return False

    top_level_domain = labels[-1]
    return len(top_level_domain) >= 2 and any(character.isalpha() for character in top_level_domain)


def _validate_url(value: str) -> dict:
    parsed = urlparse(value)
    scheme = parsed.scheme.lower()

    if scheme not in _ALLOWED_URL_SCHEMES:
        return {"valid": False, "error": "Only http:// and https:// URLs are allowed."}

    if not parsed.netloc or parsed.username or parsed.password:
        return {"valid": False, "error": "URL must include a host and must not include credentials."}

    host = parsed.hostname or ""
    host_validation = validate_target_input(host)
    if not host_validation["valid"] or host_validation["target_type"] not in {"ip", "domain", "localhost"}:
        return {"valid": False, "error": "URL host must be a valid single IPv4 address, domain, or localhost."}

    try:
        port = parsed.port
    except ValueError:
        return {"valid": False, "error": "URL port must be between 1 and 65535."}

    if port is not None and not (1 <= port <= 65535):
        return {"valid": False, "error": "URL port must be between 1 and 65535."}

    normalized_netloc = host_validation["normalized_target"]
    if port is not None:
        normalized_netloc = f"{normalized_netloc}:{port}"

    normalized = urlunparse(
        (
            scheme,
            normalized_netloc,
            parsed.path or "",
            "",
            parsed.query or "",
            "",
        )
    )

    return {
        "valid": True,
        "target_type": "url",
        "normalized_target": normalized,
    }


def validate_target_input(target: str) -> dict:
    """Validate and normalize a target string for local Target Management.

    Accepted target forms are exactly one IPv4 address, one domain, one http/https
    URL, localhost, or 127.0.0.1. Broad scopes such as CIDR blocks, IP ranges,
    wildcards, and shell-dangerous characters are rejected.
    """
    if target is None:
        return {"valid": False, "error": "Target is required."}

    value = str(target).strip()
    if not value:
        return {"valid": False, "error": "Target must not be empty."}

    if _has_dangerous_characters(value):
        return {"valid": False, "error": "Target contains shell-dangerous characters."}

    if "/" in value and not value.lower().startswith(("http://", "https://")):
        return {"valid": False, "error": "CIDR ranges are not allowed in this version."}

    if "*" in value:
        return {"valid": False, "error": "Wildcards are not allowed in this version."}

    if _looks_like_range(value):
        return {"valid": False, "error": "IP ranges are not allowed in this version."}

    lower_value = value.lower()
    if lower_value.startswith(("http://", "https://")):
        return _validate_url(value)

    if "://" in value:
        return {"valid": False, "error": "Only http:// and https:// URLs are allowed."}

    if lower_value == "localhost":
        return {"valid": True, "target_type": "localhost", "normalized_target": "localhost"}

    try:
        ipv4 = ipaddress.IPv4Address(value)
        return {"valid": True, "target_type": "ip", "normalized_target": str(ipv4)}
    except ValueError:
        pass

    normalized_domain = lower_value
    if _is_valid_domain(normalized_domain):
        return {"valid": True, "target_type": "domain", "normalized_target": normalized_domain}

    return {"valid": False, "error": "Target must be one IPv4 address, one domain, one http/https URL, localhost, or 127.0.0.1."}
