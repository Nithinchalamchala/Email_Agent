import sqlite3
import json
import os
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "sample_data", "hermes.db")
)

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id                    TEXT PRIMARY KEY,
                sender                TEXT,
                subject               TEXT,
                body                  TEXT,
                received_date         TEXT,
                is_read               INTEGER NOT NULL DEFAULT 0,
                safety                TEXT,
                source                TEXT,
                intent                TEXT,
                priority              TEXT,
                action                TEXT,
                requires_human_review INTEGER NOT NULL DEFAULT 0,
                draft                 TEXT,
                summary               TEXT,
                reasoning             TEXT,
                pipeline_output       TEXT,
                original_email        TEXT,
                processed_at          TEXT,
                source_type           TEXT
            )
        """)
        conn.commit()

def email_exists(email_id: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM emails WHERE id = ?", (email_id,)
        ).fetchone()
        return row is not None

def insert_email(record: dict):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO emails
                (id, sender, subject, body, received_date, is_read,
                 safety, source, intent, priority,
                 action, requires_human_review, draft, summary, reasoning,
                 pipeline_output, original_email, processed_at, source_type)
            VALUES
                (:id, :sender, :subject, :body, :received_date, :is_read,
                 :safety, :source, :intent, :priority,
                 :action, :requires_human_review, :draft, :summary, :reasoning,
                 :pipeline_output, :original_email, :processed_at, :source_type)
        """, record)
        conn.commit()

def get_all_emails() -> list:
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, sender, subject, body, received_date, is_read,
                   safety, source, intent, priority,
                   action, requires_human_review, reasoning,
                   processed_at, source_type
            FROM emails
            ORDER BY received_date DESC NULLS LAST
        """).fetchall()
        return [dict(row) for row in rows]

def get_email_by_id(email_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM emails WHERE id = ?", (email_id,)
        ).fetchone()
        return dict(row) if row else None

def mark_as_read(email_id: str) -> bool:
    with get_connection() as conn:
        result = conn.execute(
            "UPDATE emails SET is_read = 1 WHERE id = ?", (email_id,)
        )
        conn.commit()
        return result.rowcount > 0

# ── Date helpers for filtering ─────────────────────────────────────────────────

def _utc_midnight(days_ago: int = 0) -> str:
    """Return ISO-8601 string for midnight UTC, N days ago. No timezone suffix
    so SQLite lexicographic comparison works with stored Z-suffixed dates."""
    d = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return d.strftime('%Y-%m-%dT00:00:00')

# ── Paginated query ────────────────────────────────────────────────────────────

MAX_DEFAULT = 100   # hard cap for '7days' and 'all' views

def get_emails_paginated(
    page: int = 1,
    limit: int = 25,
    filter_type: str = "7days",
    search: str = "",
    priority: str = "",
    safety: str = "",
    action: str = "",
) -> dict:
    conditions: list[str] = []
    params: list = []

    # ── Quick filter ──────────────────────────────────────────────────────────
    if filter_type == "today":
        conditions.append("received_date >= ?")
        params.append(_utc_midnight(0))

    elif filter_type == "yesterday":
        conditions.append("received_date >= ?")
        conditions.append("received_date < ?")
        params.extend([_utc_midnight(1), _utc_midnight(0)])

    elif filter_type == "7days":
        conditions.append("received_date >= ?")
        params.append(_utc_midnight(7))

    elif filter_type == "unread":
        conditions.append("is_read = 0")

    elif filter_type == "important":
        conditions.append("(LOWER(priority) IN ('high', 'urgent') OR requires_human_review = 1)")

    elif filter_type == "ai_replied":
        conditions.append("draft IS NOT NULL AND draft != ''")

    elif filter_type == "pending_review":
        conditions.append("requires_human_review = 1")

    # "all" → no date filter (capped at MAX_DEFAULT)

    # ── Secondary filters ─────────────────────────────────────────────────────
    if search:
        conditions.append("(LOWER(subject) LIKE ? OR LOWER(sender) LIKE ?)")
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

    if priority:
        conditions.append("LOWER(priority) = ?")
        params.append(priority.lower())

    if safety:
        conditions.append("LOWER(safety) = ?")
        params.append(safety.lower())

    if action:
        conditions.append("action = ?")
        params.append(action)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_connection() as conn:
        raw_total = conn.execute(
            f"SELECT COUNT(*) FROM emails {where}", params
        ).fetchone()[0]

        # Cap to MAX_DEFAULT for broad filters; other filters return full count
        cap = MAX_DEFAULT if filter_type in ("7days", "all") else raw_total
        capped_total = min(raw_total, cap)

        offset = (page - 1) * limit
        if offset >= capped_total:
            return {"emails": [], "total": capped_total, "page": page,
                    "limit": limit, "has_more": False}

        fetch_n = min(limit, capped_total - offset)
        rows = conn.execute(
            f"""
            SELECT id, sender, subject, body, received_date, is_read,
                   safety, source, intent, priority,
                   action, requires_human_review, reasoning,
                   processed_at, source_type
            FROM emails {where}
            ORDER BY received_date DESC NULLS LAST
            LIMIT ? OFFSET ?
            """,
            params + [fetch_n, offset],
        ).fetchall()

    emails = [dict(r) for r in rows]
    return {
        "emails":   emails,
        "total":    capped_total,
        "page":     page,
        "limit":    limit,
        "has_more": (offset + len(emails)) < capped_total,
    }

# ── Global stats ───────────────────────────────────────────────────────────────

def get_stats() -> dict:
    with get_connection() as conn:
        total       = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
        unread      = conn.execute("SELECT COUNT(*) FROM emails WHERE is_read = 0").fetchone()[0]
        needs_review = conn.execute(
            "SELECT COUNT(*) FROM emails WHERE requires_human_review = 1"
        ).fetchone()[0]
        high_priority = conn.execute(
            "SELECT COUNT(*) FROM emails WHERE LOWER(priority) IN ('high', 'urgent')"
        ).fetchone()[0]
    return {
        "total":        total,
        "unread":       unread,
        "needs_review": needs_review,
        "high_priority": high_priority,
    }
