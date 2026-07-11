"""Read-only Domain Archive Intelligence helpers.

This module builds a defensive OSINT report for stored Target Management
records only. It does not scrape third-party websites, run shell commands,
perform brute force, enumerate subdomains, use wordlists, or collect personal
tracking data.
"""

from __future__ import annotations

import json
import socket

import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPORT_DIR = Path("reports/domain_archive")
SCAN_TYPE = "domain_archive"
RAW_LIMIT = 20000
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



def _extract_registrar(data: dict[str, Any]) -> str | None:
    for entity in data.get("entities") or []:
        if not isinstance(entity, dict):
            continue
        roles = entity.get("roles") or []
        if "registrar" not in roles:
            continue
        vcard = entity.get("vcardArray") or []
        if len(vcard) >= 2 and isinstance(vcard[1], list):
            for item in vcard[1]:
                if isinstance(item, list) and len(item) >= 4 and item[0] == "fn" and item[3]:
                    return str(item[3])
        if entity.get("handle"):
            return str(entity["handle"])
    return None


def _summarize_events(events: Any) -> dict[str, str | None]:
    wanted = {
        "registration": None,
        "expiration": None,
        "last changed": None,
    }
    if not isinstance(events, list):
        return wanted
    for event in events:
        if not isinstance(event, dict):
            continue
        action = str(event.get("eventAction") or "").lower()
        date = event.get("eventDate")
        if action in wanted and date:
            wanted[action] = str(date)
    return wanted


def fetch_rdap_summary(domain: str) -> dict[str, Any]:
    """Fetch a small RDAP JSON summary for a domain without scraping."""
    url = f"https://rdap.org/domain/{domain}"
    try:
        response = requests.get(url, timeout=10)
        status_code = response.status_code
        response.raise_for_status()
        data = response.json()
        raw_text = json.dumps(data, ensure_ascii=False)
        nameservers = []
        for ns in data.get("nameservers") or []:
            if isinstance(ns, dict):
                name = ns.get("ldhName") or ns.get("unicodeName")
                if name:
                    nameservers.append(str(name))
        return {
            "success": True,
            "status_code": status_code,
            "handle": data.get("handle"),
            "ldhName": data.get("ldhName"),
            "registrar": _extract_registrar(data),
            "registrar_name": _extract_registrar(data),
            "events": _summarize_events(data.get("events")),
            "nameservers": nameservers,
            "status": data.get("status") if isinstance(data.get("status"), list) else [],
            "raw_limited": raw_text[:RAW_LIMIT] if len(raw_text) <= RAW_LIMIT else raw_text[:RAW_LIMIT],
        }
    except requests.RequestException as exc:
        return {"success": False, "status_code": getattr(exc.response, "status_code", None), "error": str(exc), "raw_limited": None}
    except (ValueError, TypeError) as exc:
        return {"success": False, "status_code": None, "error": f"Invalid RDAP JSON: {exc}", "raw_limited": None}


def fetch_wayback_summary(domain: str) -> dict[str, Any]:
    """Fetch a lite Wayback CDX summary without scraping or enumeration."""
    params = {
        "url": f"{domain}/*",
        "output": "json",
        "fl": "timestamp,original,statuscode,mimetype,digest",
        "filter": "statuscode:200",
        "collapse": "digest",
        "limit": "20",
    }
    try:
        response = requests.get("https://web.archive.org/cdx", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        rows = data[1:] if isinstance(data, list) and data and isinstance(data[0], list) else []
        captures = []
        for row in rows[:20]:
            if not isinstance(row, list) or len(row) < 5:
                continue
            timestamp, original, statuscode, mimetype, _digest = row[:5]
            captures.append({
                "timestamp": timestamp,
                "original": original,
                "statuscode": statuscode,
                "mimetype": mimetype,
                "snapshot_url": f"https://web.archive.org/web/{timestamp}/{original}",
            })
        timestamps = [capture["timestamp"] for capture in captures if capture.get("timestamp")]
        return {
            "success": True,
            "total_returned": len(captures),
            "first_capture": min(timestamps) if timestamps else None,
            "last_capture": max(timestamps) if timestamps else None,
            "captures": captures,
        }
    except requests.RequestException as exc:
        return {"success": False, "error": str(exc), "total_returned": 0, "captures": []}
    except (ValueError, TypeError) as exc:
        return {"success": False, "error": f"Invalid Wayback CDX JSON: {exc}", "total_returned": 0, "captures": []}

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
            "rdap_summary": None,
            "wayback_summary": None,
            "source_links": {},
            "report_file": None,
        }

    domain = extracted["domain"]
    current_dns = _resolve_current_dns(domain)
    source_links = _build_source_links(domain)
    rdap_summary = fetch_rdap_summary(domain)
    wayback_summary = fetch_wayback_summary(domain)
    wayback_count = int(wayback_summary.get("total_returned") or 0) if wayback_summary.get("success") else 0
    rdap_available = bool(rdap_summary.get("success"))
    if wayback_count > 0:
        summary = "Domain archive report completed. Wayback captures found."
    elif not current_dns["resolved"] and rdap_available:
        summary = "Domain archive report completed. DNS does not currently resolve, but RDAP/archive sources were checked."
    else:
        summary = "Domain archive report completed. No Wayback captures returned in lite query."

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
        "rdap_summary": rdap_summary,
        "wayback_summary": wayback_summary,
        "source_links": source_links,
        "report_file": None,
    }
    _write_report(report)
    return report
