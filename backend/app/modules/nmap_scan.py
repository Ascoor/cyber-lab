"""Safe, limited Nmap Basic Scan integration.

This module only runs a fixed defensive Nmap command against a target record
that has already been loaded from local Target Management storage.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.modules.target_validation import validate_target_input

REPORT_DIR = Path("reports/nmap_basic")
SCAN_TYPE = "nmap_basic"
NMAP_TIMEOUT_SECONDS = 180


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_timestamp_for_filename(value: str) -> str:
    return value.replace(":", "").replace("+", "Z").replace(".", "_")


def _write_report(report: dict[str, Any]) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = _safe_timestamp_for_filename(report["started_at"])
    report_path = REPORT_DIR / f"target_{report['target_id']}_{timestamp}.json"
    report["report_file"] = str(report_path)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(report_path)


def write_report(report: dict[str, Any]) -> str:
    """Persist an updated scan report without changing the original location."""
    report_file = report.get("report_file")
    if report_file:
        report_path = Path(report_file)
        if report_path.is_relative_to(REPORT_DIR):
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            return str(report_path)
    return _write_report(report)


def _summarize_nmap_result(success: bool, stdout: str, stderr: str) -> str:
    if not success:
        return (stderr or "Nmap Basic scan failed.").strip()[:500]
    if "/open" in stdout or " open " in stdout:
        return "Nmap Basic completed. Open ports detected."
    if "Host is up" in stdout:
        return "Host is up. Nmap Basic completed. No open ports detected in top 100 ports."
    return "Nmap Basic completed. No open ports detected in top 100 ports."


def run_basic_nmap_scan_for_target(target_record: dict) -> dict:
    """Run a fixed Nmap Basic scan for one stored target record.

    The caller must pass a target record fetched from SQLite. This function does
    not accept direct user target text, flags, options, CIDR ranges, or scripts.
    """
    started_at = _utc_now()

    if not isinstance(target_record, dict):
        finished_at = _utc_now()
        return {
            "success": False,
            "target_id": None,
            "target": None,
            "target_type": None,
            "scan_type": SCAN_TYPE,
            "command_used": [],
            "report_file": None,
            "summary": "Invalid target_record: expected a dictionary loaded from Target Management.",
            "stdout": "",
            "stderr": "Invalid target_record: expected a dictionary loaded from Target Management.",
            "started_at": started_at,
            "finished_at": finished_at,
        }

    target_id = target_record.get("id")
    target = target_record.get("target")
    target_type = target_record.get("target_type")

    validation = validate_target_input(target)
    if not validation["valid"]:
        finished_at = _utc_now()
        return {
            "success": False,
            "target_id": target_id,
            "target": target,
            "target_type": target_type,
            "scan_type": SCAN_TYPE,
            "command_used": [],
            "report_file": None,
            "summary": validation["error"],
            "stdout": "",
            "stderr": validation["error"],
            "started_at": started_at,
            "finished_at": finished_at,
        }

    normalized_target = validation["normalized_target"]
    command = ["nmap", "-sV", "-T3", "--top-ports", "100", normalized_target]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=NMAP_TIMEOUT_SECONDS,
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        success = completed.returncode == 0
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        stderr = f"{stderr}\nNmap Basic scan timed out after {NMAP_TIMEOUT_SECONDS} seconds.".strip()
        success = False
    except FileNotFoundError:
        stdout = ""
        stderr = "nmap binary was not found in PATH. Install nmap to run this scan."
        success = False

    finished_at = _utc_now()
    report = {
        "success": success,
        "target_id": target_id,
        "target": normalized_target,
        "target_type": validation["target_type"],
        "scan_type": SCAN_TYPE,
        "command_used": command,
        "report_file": None,
        "summary": _summarize_nmap_result(success, stdout, stderr),
        "stdout": stdout,
        "stderr": stderr,
        "started_at": started_at,
        "finished_at": finished_at,
    }
    _write_report(report)
    return report
