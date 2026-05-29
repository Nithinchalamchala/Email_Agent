"""
One-time migration: import all existing JSON result files into SQLite.

Run from the project root:
    python -m storage.migrate
"""
import os
import json
import re
from datetime import datetime, timezone

from storage.database import init_db, insert_email

_BASE = os.path.join(os.path.dirname(__file__), "..")
SAMPLE_DATA   = os.path.abspath(os.path.join(_BASE, "sample_data"))
BATCH_DIR     = os.path.join(SAMPLE_DATA, "batch")
RESULTS_DIR   = os.path.join(BATCH_DIR, "results")
OUTPUTDRAFT_DIR = os.path.join(BATCH_DIR, "outputdraft")
READ_STATE_PATH = os.path.join(SAMPLE_DATA, "read_state.json")

def _try_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None

def _strip_html(html):
    if not html:
        return ""
    return re.sub('<[^<]+?>', '', html).strip()

def _build_record(email_id, result, orig, source_type, read_state):
    clf = result.get("classification", {}) or {}

    subject = (
        result.get("original_subject")
        or (orig.get("subject") if orig else None)
        or result.get("subject", "")
    )
    sender = (
        result.get("original_sender")
        or (orig.get("sender") if orig else None)
        or clf.get("source", "unknown")
    )
    body = (
        result.get("original_body")
        or (orig.get("body") if orig else None)
        or ""
    )
    if not body and orig:
        full = orig.get("full_msg") or {}
        body = _strip_html(full.get("body", {}).get("content", ""))

    received_date = (
        result.get("original_timestamp")
        or (orig.get("timestamp") if orig else None)
        or (
            orig.get("summary", {}).get("receivedDateTime")
            if orig and isinstance(orig.get("summary"), dict) else None
        )
    )

    # Keep only pipeline-specific keys in the JSON blob
    keep = {"classification", "action", "draft", "summary",
            "reasoning", "requires_human_review", "llm_classification"}
    pipeline_output = {k: v for k, v in result.items() if k in keep}

    return {
        "id":                    email_id,
        "sender":                sender or "",
        "subject":               subject or "",
        "body":                  body or "",
        "received_date":         received_date,
        "is_read":               1 if read_state.get(email_id) else 0,
        "safety":                clf.get("safety", ""),
        "source":                clf.get("source", ""),
        "intent":                clf.get("intent", ""),
        "priority":              clf.get("priority", ""),
        "action":                result.get("action", ""),
        "requires_human_review": 1 if result.get("requires_human_review") else 0,
        "draft":                 result.get("draft"),
        "summary":               result.get("summary"),
        "reasoning":             result.get("reasoning"),
        "pipeline_output":       json.dumps(pipeline_output),
        "original_email":        json.dumps(orig) if orig else None,
        "processed_at":          received_date or datetime.now(timezone.utc).isoformat(),
        "source_type":           source_type,
    }

def _migrate_folder(results_dir, orig_base, source_type, read_state):
    if not os.path.exists(results_dir):
        print(f"  (not found, skipping): {results_dir}")
        return 0
    files = [f for f in os.listdir(results_dir) if f.endswith(".json")]
    count = 0
    for fname in files:
        result = _try_json(os.path.join(results_dir, fname))
        if not result:
            continue
        email_id = fname.replace("_result.json", "").replace(".json", "")
        orig = _try_json(os.path.join(orig_base, f"{email_id}.json"))
        record = _build_record(email_id, result, orig, source_type, read_state)
        insert_email(record)
        count += 1
        print(f"  + {email_id}")
    return count

def main():
    print("Initializing database...")
    init_db()

    read_state = _try_json(READ_STATE_PATH) or {}
    if read_state:
        print(f"Found read_state.json ({len(read_state)} entries) — preserving read status")

    print(f"\nMigrating batch test results ({RESULTS_DIR})...")
    n1 = _migrate_folder(RESULTS_DIR, BATCH_DIR, "batch_test", read_state)
    print(f"  {n1} records inserted")

    print(f"\nMigrating O365 output drafts ({OUTPUTDRAFT_DIR})...")
    n2 = _migrate_folder(OUTPUTDRAFT_DIR, BATCH_DIR, "o365", read_state)
    print(f"  {n2} records inserted")

    db_path = os.path.abspath(os.path.join(_BASE, "sample_data", "hermes.db"))
    print(f"\nDone: {n1 + n2} emails imported into {db_path}")
    if n1 + n2 > 0:
        print("\nYou can now delete the JSON result files from:")
        print(f"  {RESULTS_DIR}")
        print(f"  {OUTPUTDRAFT_DIR}")

if __name__ == "__main__":
    main()
