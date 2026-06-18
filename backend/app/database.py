"""SQLite persistence helpers for Cyber Lab Control Panel."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DATABASE_PATH = Path("data/cyber_lab.db")
REPORTS_ROOT = Path("reports").resolve()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                target_type TEXT NOT NULL CHECK(target_type IN ('ip', 'domain', 'url', 'localhost')),
                authorized INTEGER NOT NULL DEFAULT 0 CHECK(authorized IN (0, 1)),
                scope_notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                target TEXT NOT NULL,
                target_type TEXT,
                scan_type TEXT NOT NULL,
                status TEXT NOT NULL,
                success INTEGER NOT NULL DEFAULT 0,
                report_file TEXT,
                summary TEXT,
                started_at TEXT,
                finished_at TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def _row_to_target(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "target": row["target"],
        "target_type": row["target_type"],
        "authorized": bool(row["authorized"]),
        "scope_notes": row["scope_notes"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_target(
    *,
    name: str,
    target: str,
    target_type: str,
    authorized: bool = False,
    scope_notes: Optional[str] = None,
) -> dict[str, Any]:
    now = _utc_now()
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO targets (name, target, target_type, authorized, scope_notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), target, target_type, int(authorized), scope_notes, now, now),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM targets WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _row_to_target(row)


def list_targets() -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute("SELECT * FROM targets ORDER BY id ASC").fetchall()
    return [_row_to_target(row) for row in rows]


def get_target(target_id: int) -> Optional[dict[str, Any]]:
    with _connect() as connection:
        row = connection.execute("SELECT * FROM targets WHERE id = ?", (target_id,)).fetchone()
    if row is None:
        return None
    return _row_to_target(row)


def update_target_authorization(target_id: int, authorized: bool) -> Optional[dict[str, Any]]:
    now = _utc_now()
    with _connect() as connection:
        cursor = connection.execute(
            "UPDATE targets SET authorized = ?, updated_at = ? WHERE id = ?",
            (int(authorized), now, target_id),
        )
        if cursor.rowcount == 0:
            return None
        connection.commit()
        row = connection.execute("SELECT * FROM targets WHERE id = ?", (target_id,)).fetchone()
    return _row_to_target(row)


def delete_target(target_id: int) -> bool:
    with _connect() as connection:
        cursor = connection.execute("DELETE FROM targets WHERE id = ?", (target_id,))
        connection.commit()
    return cursor.rowcount > 0


def _row_to_scan(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "scan_id": row["id"],
        "target_id": row["target_id"],
        "target": row["target"],
        "target_type": row["target_type"],
        "scan_type": row["scan_type"],
        "status": row["status"],
        "success": bool(row["success"]),
        "report_file": row["report_file"],
        "summary": row["summary"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "created_at": row["created_at"],
    }


def create_scan_record(
    *,
    target_id: Optional[int],
    target: str,
    target_type: Optional[str],
    scan_type: str,
    status: str,
    success: bool,
    report_file: Optional[str],
    summary: Optional[str],
    started_at: Optional[str],
    finished_at: Optional[str],
) -> dict[str, Any]:
    now = _utc_now()
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO scans (
                target_id, target, target_type, scan_type, status, success,
                report_file, summary, started_at, finished_at, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                target_id,
                target,
                target_type,
                scan_type,
                status,
                int(success),
                report_file,
                summary,
                started_at,
                finished_at,
                now,
            ),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM scans WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _row_to_scan(row)


def list_scan_records(limit: int = 50) -> list[dict[str, Any]]:
    safe_limit = max(1, min(int(limit), 200))
    with _connect() as connection:
        rows = connection.execute("SELECT * FROM scans ORDER BY id DESC LIMIT ?", (safe_limit,)).fetchall()
    return [_row_to_scan(row) for row in rows]


def get_scan_record(scan_id: int) -> Optional[dict[str, Any]]:
    with _connect() as connection:
        row = connection.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    if row is None:
        return None
    return _row_to_scan(row)


def _safe_report_path(report_file: str) -> Optional[Path]:
    if not report_file:
        return None
    report_path = Path(report_file)
    if report_path.is_absolute():
        return None
    resolved = report_path.resolve()
    try:
        resolved.relative_to(REPORTS_ROOT)
    except ValueError:
        return None
    return resolved


def get_scan_report_by_id(scan_id: int) -> Optional[dict[str, Any]]:
    scan = get_scan_record(scan_id)
    if scan is None:
        return None
    report_path = _safe_report_path(scan.get("report_file") or "")
    if report_path is None or not report_path.is_file():
        return None
    return json.loads(report_path.read_text(encoding="utf-8"))
