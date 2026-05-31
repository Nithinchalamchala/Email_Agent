import json
import sys
import os
import base64

# Ensure project root is on sys.path regardless of where uvicorn is launched from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from storage.database import (
    init_db,
    get_emails_paginated,
    get_stats,
    get_email_by_id,
    mark_as_read,
)

init_db()

from datetime import datetime as _dt

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _serialize(e: dict) -> dict:
    return {
        "id":                    e["id"],
        "sender":                e["sender"] or "",
        "subject":               e["subject"] or "",
        "body":                  e["body"] or "",
        "action":                e["action"] or "",
        "requires_human_review": bool(e["requires_human_review"]),
        "intent":                e["intent"] or "",
        "priority":              e["priority"] or "",
        "safety":                e["safety"] or "safe",
        "reasoning":             e["reasoning"] or "",
        "received_date":         e["received_date"],
        "is_read":               bool(e["is_read"]),
        "source_type":           e["source_type"] or "",
    }

@app.get("/api/batch")
def list_batch_results(
    page: int     = 1,
    limit: int    = 25,
    filter: str   = "7days",
    search: str   = "",
    priority: str = "",
    safety: str   = "",
    action: str   = "",
):
    result = get_emails_paginated(
        page=page,
        limit=min(limit, 50),       # never exceed 50 per page
        filter_type=filter,
        search=search,
        priority=priority,
        safety=safety,
        action=action,
    )
    return {
        "results":  [_serialize(e) for e in result["emails"]],
        "total":    result["total"],
        "page":     result["page"],
        "limit":    result["limit"],
        "has_more": result["has_more"],
    }

@app.get("/api/stats")
def email_stats():
    return get_stats()

@app.get("/api/email/{email_id}")
def get_email_result(email_id: str):
    email = get_email_by_id(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found.")

    pipeline_output: dict = {}
    if email.get("pipeline_output"):
        try:
            pipeline_output = json.loads(email["pipeline_output"])
        except Exception:
            pass

    original_email: dict = {}
    if email.get("original_email"):
        try:
            original_email = json.loads(email["original_email"])
        except Exception:
            pass

    result = {**pipeline_output}
    result["original_subject"] = email["subject"]
    result["original_body"]    = email["body"]
    result["original_sender"]  = email["sender"]
    result["received_date"]    = email["received_date"]
    result["is_read"]          = bool(email["is_read"])
    result["source_type"]      = email["source_type"]

    if original_email:
        result["thread_id"] = original_email.get("thread_id")
        result["metadata"]  = original_email.get("metadata")
        html_body = (
            original_email.get("raw_html_body")
            or original_email.get("original_html_body")
            or (
                (original_email.get("full_msg") or {}).get("body", {}).get("content")
                if isinstance(original_email.get("full_msg"), dict) else None
            )
        )
        if html_body:
            result["original_html_body"] = html_body

    return result

@app.patch("/api/email/{email_id}/mark-read")
def mark_email_read(email_id: str):
    if not mark_as_read(email_id):
        raise HTTPException(status_code=404, detail="Email not found.")
    return {"success": True, "email_id": email_id, "is_read": True}

@app.post("/api/fetch-emails")
def fetch_emails(
    x_ms_graph_token: str | None = Header(default=None, alias="X-MS-GRAPH-TOKEN"),
):
    if not x_ms_graph_token:
        raise HTTPException(
            status_code=401,
            detail="X-MS-GRAPH-TOKEN header is required. Sign in via the dashboard first.",
        )
    try:
        from services.graph_fetcher import fetch_and_process
        results = fetch_and_process(token=x_ms_graph_token, limit=10)
        return {
            "success":   True,
            "processed": len(results["processed"]),
            "skipped":   len(results["skipped"]),
            "emails":    results["processed"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.get("/api/sync-status")
def sync_status():
    from storage.database import get_connection
    with get_connection() as conn:
        row = conn.execute(
            "SELECT processed_at FROM emails ORDER BY processed_at DESC LIMIT 1"
        ).fetchone()
    last_sync = row["processed_at"] if row else None

    user_email        = ""
    connected_account = "Not connected"

    try:
        from auth.msal_auth import get_authenticated_user
        msal_user = get_authenticated_user()
        if msal_user.get("email"):
            user_email        = msal_user["email"]
            connected_account = "Outlook"
    except Exception:
        pass

    if not user_email:
        token = os.environ.get("MS_GRAPH_TOKEN", "")
        if token:
            try:
                payload_b64 = token.split(".")[1]
                payload_b64 += "=" * (4 - len(payload_b64) % 4)
                decoded = json.loads(base64.b64decode(payload_b64))
                user_email = (
                    decoded.get("upn")
                    or decoded.get("preferred_username")
                    or decoded.get("unique_name")
                    or ""
                )
                if user_email:
                    connected_account = "Outlook"
            except Exception:
                pass

    return {
        "last_sync":         last_sync,
        "ai_status":         "active",
        "connected_account": connected_account,
        "user_email":        user_email or "",
    }


# ── Calendar endpoints ─────────────────────────────────────────────────────────

@app.get("/api/calendar/calendars")
def api_get_calendars(x_cal_token: str | None = Header(default=None, alias="X-Cal-Token")):
    try:
        from cal.graph_client import get_calendars
        return get_calendars(token=x_cal_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calendar/events")
def api_get_events(days: int = 7, x_cal_token: str | None = Header(default=None, alias="X-Cal-Token")):
    try:
        from cal.graph_client import get_upcoming_events
        return get_upcoming_events(days=days, token=x_cal_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calendar/run")
def api_run_calendar_pipeline(body: dict, x_cal_token: str | None = Header(default=None, alias="X-Cal-Token")):
    try:
        from cal.calendar_pipeline import run_calendar_pipeline
        email = {
            "sender": body.get("sender", ""),
            "subject": body.get("subject", ""),
            "cleaned_body": body.get("body", ""),
            "timestamp": body.get("timestamp") or _dt.utcnow().isoformat(),
        }
        return run_calendar_pipeline(email, token=x_cal_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/email/smart-reply")
def api_smart_reply(body: dict, x_cal_token: str | None = Header(default=None, alias="X-Cal-Token")):
    """Generate an availability-aware draft reply using real calendar context."""
    try:
        from cal.smart_reply import generate_smart_reply
        return generate_smart_reply(email=body, token=x_cal_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
