"""Read-only Domain Archive Intelligence helpers.

This module builds a defensive OSINT report for stored Target Management
records only. It does not scrape third-party websites, run shell commands,
perform brute force, enumerate subdomains, use wordlists, or collect personal
tracking data.
"""

from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPORT_DIR = Path("reports/domain_archive")
SCAN_TYPE = "domain_archive"
DOMAIN_REQUIRED_MESSAGE = "Domain Archive Intelligence requires a domain or URL target."


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_timestamp_for_filename(value: str) -> str:
    return value.replace(":", "").replace("+", "Z").replace(".", "_")


def _safe_domain_for_filename(domain: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "."} else "_" for char in domain).strip("._") or "domain"


def _write_report(report: dict[str, Any]) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = _safe_timestamp_for_filename(report["started_at"])
    safe_domain = _safe_domain_for_filename(report.get("domain") or "domain")
    report_path = REPORT_DIR / f"target_{report['target_id']}_{safe_domain}_{timestamp}.json"
    report["report_file"] = str(report_path)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(report_path)


def write_report(report: dict[str, Any]) -> str:
    """Persist an updated archive report without changing the original path."""
    report_file = report.get("report_file")
    if report_file:
        report_path = Path(report_file)
        if report_path.is_relative_to(REPORT_DIR):
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            return str(report_path)
    return _write_report(report)


def extract_domain_from_target(target_record: dict) -> dict:
    """Extract a domain hostname from a stored target record.

    Domain Archive Intelligence accepts only Target Management records with
    target_type `domain` or `url`. IP and localhost targets are rejected because
    the module is intended for domain archival context.
    """
    if not isinstance(target_record, dict):
        return {"success": False, "error": "Invalid target_record: expected a dictionary loaded from Target Management."}

    target = str(target_record.get("target") or "").strip()
    target_type = str(target_record.get("target_type") or "").strip().lower()

    if target_type == "domain":
        domain = target.rstrip(".").lower()
    elif target_type == "url":
        parsed = urlparse(target)
        domain = (parsed.hostname or "").rstrip(".").lower()
    elif target_type in {"localhost", "ip"}:
        return {"success": False, "error": DOMAIN_REQUIRED_MESSAGE}
    else:
        return {"success": False, "error": DOMAIN_REQUIRED_MESSAGE}

    if not domain:
        return {"success": False, "error": DOMAIN_REQUIRED_MESSAGE}

    return {"success": True, "domain": domain, "target_type": target_type, "original_target": target}


def _resolve_current_dns(domain: str) -> dict[str, Any]:
    try:
        hostname, aliases, addresses = socket.gethostbyname_ex(domain)
        return {
            "resolved": True,
            "hostname": hostname,
            "aliases": aliases,
            "ipv4_addresses": sorted(set(addresses)),
            "error": None,
        }
    except socket.gaierror as exc:
        return {
            "resolved": False,
            "hostname": domain,
            "aliases": [],
            "ipv4_addresses": [],
            "error": str(exc),
        }


def _build_source_links(domain: str) -> dict[str, str]:
    return {
        "wayback_url": f"https://web.archive.org/web/*/{domain}",
        "crtsh_url": f"https://crt.sh/?q={domain}",
        "rdap_url": f"https://rdap.org/domain/{domain}",
        "whoisxml_history_note": "WHOIS history may require a paid API such as WhoisXML API or DomainTools.",
        "whoisfreaks_dns_history_url": "https://whoisfreaks.com/tools/dns/history/lookup",
        "whoisfreaks_whois_history_url": "https://whoisfreaks.com/tools/whois/history/lookup",
    }


def run_domain_archive_lookup_for_target(target_record: dict) -> dict:
    """Build and save a read-only Domain Archive Intelligence report."""
    started_at = _utc_now()
    target_id = target_record.get("id") if isinstance(target_record, dict) else None
    original_target = target_record.get("target") if isinstance(target_record, dict) else None
    target_type = target_record.get("target_type") if isinstance(target_record, dict) else None

    extracted = extract_domain_from_target(target_record)
    if not extracted.get("success"):
        finished_at = _utc_now()
        return {
            "success": False,
            "target_id": target_id,
            "original_target": original_target,
            "domain": None,
            "target_type": target_type,
            "scan_type": SCAN_TYPE,
            "started_at": started_at,
            "finished_at": finished_at,
            "summary": extracted.get("error") or DOMAIN_REQUIRED_MESSAGE,
            "current_dns": None,
            "source_links": {},
            "report_file": None,
        }

    domain = extracted["domain"]
    current_dns = _resolve_current_dns(domain)
    source_links = _build_source_links(domain)
    if current_dns["resolved"]:
        summary = f"Domain Archive Intelligence report built for {domain}. Current DNS resolved to {len(current_dns['ipv4_addresses'])} IPv4 address(es)."
    else:
        summary = f"Domain Archive Intelligence report built for {domain}. The domain does not currently resolve via DNS."

    finished_at = _utc_now()
    report = {
        "success": True,
        "target_id": target_id,
        "original_target": extracted["original_target"],
        "domain": domain,
        "target_type": extracted["target_type"],
        "scan_type": SCAN_TYPE,
        "started_at": started_at,
        "finished_at": finished_at,
        "summary": summary,
        "current_dns": current_dns,
        "source_links": source_links,
        "report_file": None,
    }
    _write_report(report)
    return report
