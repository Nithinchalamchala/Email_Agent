"""
Shared Microsoft Graph email fetch + pipeline service.

Used by:
  - dashboard/app.py  POST /api/fetch-emails   (browser SPA flow — token from React)
  - fetch_unread_o365.py                        (CLI fallback — token from Device Code)
"""
import json
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from pipeline.orchestrator import email_pipeline
from storage.database import insert_email, email_exists

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Prefer": 'outlook.body-content-type="text"',
    }


def _html_to_text(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n", strip=True)


def _get_email_body(msg_id: str, token: str) -> tuple[dict, dict]:
    url  = f"{GRAPH_BASE}/me/messages/{msg_id}?$select=body,subject"
    resp = requests.get(url, headers=_headers(token), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data, data.get("body", {})


def fetch_unread_from_graph(token: str, limit: int = 10) -> list[dict]:
    """Fetch unread emails from /me/messages and return as list of dicts."""
    url = (
        f"{GRAPH_BASE}/me/messages?"
        f"$filter=isRead eq false&$top={limit}"
        "&$select=id,sender,subject,receivedDateTime,conversationId,internetMessageId"
    )
    resp = requests.get(url, headers=_headers(token), timeout=15)
    resp.raise_for_status()

    emails = []
    for item in resp.json().get("value", []):
        full_msg, body_obj = _get_email_body(item["id"], token)
        html_body  = body_obj.get("content", "")
        plain_body = _html_to_text(html_body) if html_body else ""
        if not plain_body and html_body:
            plain_body = "[HTML body — see original_html_body]"
        emails.append({
            "sender":        (item.get("sender") or {}).get("emailAddress", {}).get("address", ""),
            "subject":       item.get("subject") or full_msg.get("subject", ""),
            "body":          plain_body,
            "timestamp":     item.get("receivedDateTime", datetime.utcnow().isoformat()),
            "thread_id":     item.get("conversationId", ""),
            "metadata": {
                "id":                item.get("id", ""),
                "internetMessageId": item.get("internetMessageId", ""),
            },
            "raw_html_body": html_body,
            "full_msg":      full_msg,
        })
    return emails


def process_and_save(emails: list[dict]) -> dict:
    """Run each email through the pipeline and persist to DB. Returns a summary."""
    processed: list[dict] = []
    skipped:   list[str]  = []

    for email in emails:
        email_id = email["metadata"].get("id") or email["thread_id"]

        if email_exists(email_id):
            skipped.append(email_id)
            continue

        result = email_pipeline(email)
        clf    = result.get("classification", {}) or {}

        pipeline_output = {
            k: result[k]
            for k in ("classification", "action", "draft", "summary",
                      "reasoning", "requires_human_review")
            if k in result
        }
        if result.get("llm_classification"):
            pipeline_output["llm_classification"] = result["llm_classification"]

        insert_email({
            "id":                    email_id,
            "sender":                email.get("sender", ""),
            "subject":               email.get("subject", ""),
            "body":                  email.get("body", ""),
            "received_date":         email.get("timestamp"),
            "is_read":               0,
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
            "original_email":        json.dumps(email),
            "processed_at":          datetime.now(timezone.utc).isoformat(),
            "source_type":           "o365",
        })
        processed.append({
            "id":      email_id,
            "subject": email.get("subject", ""),
            "action":  result.get("action", ""),
        })

    return {"processed": processed, "skipped": skipped}


def fetch_and_process(token: str, limit: int = 10) -> dict:
    """End-to-end: fetch from Graph + run through pipeline + save to DB."""
    emails = fetch_unread_from_graph(token, limit)
    return process_and_save(emails)
