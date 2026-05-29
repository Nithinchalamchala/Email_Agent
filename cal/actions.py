"""
Executes calendar actions against the Microsoft Graph API: create event, update event,
delete event, accept/decline invite. Receives structured CalendarEvent objects and
returns success/failure status with the Graph API response payload.
"""
from datetime import datetime, timedelta, timezone
from cal.graph_client import check_conflicts, create_event


def _build_graph_payload(extracted: dict) -> dict:
    payload = {
        "subject": extracted.get("title", "Meeting"),
        "start": {
            "dateTime": extracted["start_time"],
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": extracted["end_time"],
            "timeZone": "UTC",
        },
        "body": {
            "contentType": "Text",
            "content": extracted.get("description", ""),
        },
    }
    if extracted.get("location"):
        payload["location"] = {"displayName": extracted["location"]}
    attendees = extracted.get("attendees", [])
    if attendees:
        payload["attendees"] = [
            {"emailAddress": {"address": addr}, "type": "required"}
            for addr in attendees
        ]
    return payload


def execute_action(extracted: dict, token: str | None = None) -> dict:
    """
    Decides what to do with the extracted event:
    - confidence < 0.5  → no_action (not a clear meeting request)
    - missing times     → no_action
    - conflict exists   → conflict_detected (human review needed)
    - clear slot        → create the event via Graph API

    Returns { action, status, details }.
    """
    confidence = extracted.get("confidence", 0.0)

    if confidence < 0.5:
        return {
            "action": "no_action",
            "status": "skipped",
            "details": {"reason": f"Low confidence ({confidence:.2f}) — not a clear meeting request"},
        }

    start = extracted.get("start_time")
    end = extracted.get("end_time")

    if not start:
        return {
            "action": "no_action",
            "status": "skipped",
            "details": {"reason": "Missing start_time — cannot check or create event"},
        }

    # Default to 1-hour duration when end_time is not specified
    if not end:
        end = (datetime.fromisoformat(start) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        extracted = {**extracted, "end_time": end}

    if check_conflicts(start, end, token=token):
        return {
            "action": "conflict_detected",
            "status": "conflict",
            "details": {
                "message": "A conflicting event already exists in this time slot",
                "start": start,
                "end": end,
            },
        }

    payload = _build_graph_payload(extracted)
    graph_response = create_event(payload, token=token)

    return {
        "action": "event_created",
        "status": "success",
        "details": graph_response,
    }
