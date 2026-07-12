"""Network connectivity diagnostics for external read-only integrations.

The diagnostics in this module verify whether the local Cyber Lab runtime can
reach the public services used by Domain Archive Intelligence. They do not scan
user targets, enumerate infrastructure, accept arbitrary URLs, or run shell
commands.
"""

from __future__ import annotations

import socket
from datetime import datetime, timezone
from typing import Any

import requests

DIAGNOSTIC_TIMEOUT_SECONDS = 5
DNS_TEST_HOSTS = ("rdap.org", "web.archive.org")
HTTP_TESTS = (
    {
        "name": "rdap_org",
        "url": "https://rdap.org/domain/example.com",
        "expected_statuses": {200, 404},
    },
    {
        "name": "wayback_cdx",
        "url": "https://web.archive.org/cdx?url=example.com/*&output=json&limit=1",
        "expected_statuses": {200},
    },
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_dns(hostname: str) -> dict[str, Any]:
    try:
        addresses = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
        ip_addresses = sorted({item[4][0] for item in addresses})
        return {
            "name": hostname,
            "success": True,
            "ip_addresses": ip_addresses,
            "error": None,
        }
    except socket.gaierror as exc:
        return {
            "name": hostname,
            "success": False,
            "ip_addresses": [],
            "error": str(exc),
        }


def _check_http(test: dict[str, Any]) -> dict[str, Any]:
    try:
        response = requests.get(test["url"], timeout=DIAGNOSTIC_TIMEOUT_SECONDS)
        expected_statuses = set(test.get("expected_statuses") or {200})
        return {
            "name": test["name"],
            "success": response.status_code in expected_statuses,
            "url": test["url"],
            "status_code": response.status_code,
            "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "error": None,
        }
    except requests.RequestException as exc:
        return {
            "name": test["name"],
            "success": False,
            "url": test["url"],
            "status_code": getattr(exc.response, "status_code", None),
            "elapsed_ms": None,
            "error": str(exc),
        }


def run_network_connectivity_diagnostics() -> dict[str, Any]:
    """Run bounded diagnostics for Cyber Lab's external read-only sources."""
    started_at = _utc_now()
    dns_checks = [_check_dns(hostname) for hostname in DNS_TEST_HOSTS]
    http_checks = [_check_http(test) for test in HTTP_TESTS]
    finished_at = _utc_now()
    all_checks = dns_checks + http_checks
    success = all(check["success"] for check in all_checks)
    return {
        "success": success,
        "status": "ok" if success else "degraded",
        "scan_type": "network_connectivity_diagnostics",
        "started_at": started_at,
        "finished_at": finished_at,
        "timeout_seconds": DIAGNOSTIC_TIMEOUT_SECONDS,
        "summary": "External read-only sources are reachable." if success else "One or more external read-only sources are not reachable from this environment.",
        "dns_checks": dns_checks,
        "http_checks": http_checks,
        "notes": [
            "Diagnostics use fixed service URLs only.",
            "No user target is scanned and no shell command is executed.",
        ],
    }
