from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json

def get_batch_folders():
    base = os.path.join(os.path.dirname(__file__), "..", "sample_data", "batch")
    return [
        os.path.abspath(os.path.join(base, "results")),
        os.path.abspath(os.path.join(base, "outputdraft")),
    ]

def try_read_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None

def extract_original_fields(data, orig):
    # Try all placements for subject/body/sender/time
    result = {
        "original_subject": None,
        "original_body": None,
        "original_sender": None,
        "received_date": None
    }
    if orig:
        result["original_subject"] = orig.get("subject") or (orig.get("summary", {}).get("subject") if isinstance(orig.get("summary"), dict) else None)
        result["original_body"] = orig.get("body")
        if not result["original_body"]:
            # Try extract from full_msg if present (O365 structure)
            full = orig.get("full_msg")
            if full and isinstance(full, dict):
                body_html = full.get("body", {}).get("content")
                if body_html:
                    import re
                    plain = re.sub('<[^<]+?>', '', body_html)
                    result["original_body"] = plain.strip()
        sender = orig.get("sender")
        if not sender:
            s = orig.get("summary", {}).get("sender") if isinstance(orig.get("summary"), dict) else None
            if s and isinstance(s, dict):
                sender = s.get("emailAddress", {}).get("address") or s.get("emailAddress", {}).get("name")
        result["original_sender"] = sender or orig.get("sender")
        result["received_date"] = orig.get("timestamp") or orig.get("summary", {}).get("receivedDateTime")
    else:
        # Result JSON written by fetch_unread_o365.py already has original_* at top level
        result["original_subject"] = (
            data.get("original_subject")
            or data.get("subject")
            or (data.get("draft", "").split('\n', 1)[0].replace('Subject:', '').strip() if data.get("draft") else None)
        )
        result["original_body"] = data.get("original_body") or data.get("body") or ""
        result["original_sender"] = data.get("original_sender") or ""
        result["received_date"] = data.get("original_timestamp") or data.get("received_date")
    return result

from datetime import datetime as _dt

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/batch")
def list_batch_results():
    batchdirs = get_batch_folders()
    summaries = []
    for RESULTS_DIR in batchdirs:
        if not os.path.exists(RESULTS_DIR):
            continue
        files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")]
        for fname in files:
            fpath = os.path.join(RESULTS_DIR, fname)
            data = try_read_json(fpath)
            if not data:
                continue
            # Find possible original email file
            batch_base = os.path.dirname(RESULTS_DIR)
            email_id = fname.replace("_result.json", "").replace(".json", "")
            orig_path = os.path.join(batch_base, f"{email_id}.json")
            orig = try_read_json(orig_path)
            orig_fields = extract_original_fields(data, orig)
            summaries.append({
                "id": email_id,
                "sender": orig_fields["original_sender"] or data.get("classification", {}).get("source", "unknown"),
                "subject": orig_fields["original_subject"] or data.get("subject", "") or data.get("draft", ""),
                "body": orig_fields["original_body"] or "",
                "action": data.get("action", ""),
                "requires_human_review": data.get("requires_human_review", False),
                "intent": data.get("classification", {}).get("intent", ""),
                "priority": data.get("classification", {}).get("priority", ""),
                "safety": data.get("classification", {}).get("safety", "safe"),
                "reasoning": data.get("reasoning", ""),
                "received_date": orig_fields["received_date"],
            })
    return {"results": summaries}

@app.get("/api/email/{email_id}")
def get_email_result(email_id: str):
    batchdirs = get_batch_folders()
    for RESULTS_DIR in batchdirs:
        path = os.path.join(RESULTS_DIR, f"{email_id}_result.json")
        if os.path.exists(path):
            data = try_read_json(path) or {}
            orig_path = os.path.join(os.path.dirname(RESULTS_DIR), f"{email_id}.json")
            orig = try_read_json(orig_path)
            orig_fields = extract_original_fields(data, orig)
            # Promote fields to top-level for frontend simplicity
            data["original_subject"] = orig_fields["original_subject"]
            data["original_body"] = orig_fields["original_body"]
            data["original_sender"] = orig_fields["original_sender"]
            data["received_date"] = orig_fields["received_date"]
            return data
    raise HTTPException(status_code=404, detail="Result not found.")


# ── Calendar endpoints ─────────────────────────────────────────────────────────

@app.get("/api/calendar/calendars")
def api_get_calendars():
    try:
        from cal.graph_client import get_calendars
        return get_calendars()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calendar/events")
def api_get_events(days: int = 7):
    try:
        from cal.graph_client import get_upcoming_events
        return get_upcoming_events(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calendar/run")
def api_run_calendar_pipeline(body: dict):
    try:
        from cal.calendar_pipeline import run_calendar_pipeline
        email = {
            "sender": body.get("sender", ""),
            "subject": body.get("subject", ""),
            "cleaned_body": body.get("body", ""),
            "timestamp": body.get("timestamp") or _dt.utcnow().isoformat(),
        }
        return run_calendar_pipeline(email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
