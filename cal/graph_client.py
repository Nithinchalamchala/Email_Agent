"""
Low-level Microsoft Graph API client for calendar endpoints (/me/events, /me/calendar).
Uses the MS_GRAPH_TOKEN delegated bearer token from .env — the same token used by
fetch_unread_o365.py. All methods return raw Graph API response dicts.
"""
import json
import os
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

_BASE = "https://graph.microsoft.com/v1.0"


def _headers() -> dict:
    token = os.environ.get("MS_GRAPH_TOKEN")
    if not token:
        raise EnvironmentError("MS_GRAPH_TOKEN must be set in .env")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _raise_for_status(response: requests.Response) -> None:
    if not response.ok:
        raise RuntimeError(
            f"Graph API error {response.status_code} "
            f"[{response.request.method} {response.request.url}]: {response.text}"
        )


def get_calendars() -> dict:
    """GET /me/calendars — list all calendars for the authenticated user."""
    response = requests.get(f"{_BASE}/me/calendars", headers=_headers())
    _raise_for_status(response)
    return response.json()


def get_upcoming_events(days: int = 7) -> dict:
    """GET /me/calendarView — fetch events within the next `days` days."""
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)
    params = {
        "startDateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "$orderby": "start/dateTime",
        "$top": 50,
    }
    response = requests.get(f"{_BASE}/me/calendarView", headers=_headers(), params=params)
    _raise_for_status(response)
    return response.json()


def create_event(event_data: dict) -> dict:
    """POST /me/events — create a calendar event. event_data must follow the Graph API event schema."""
    response = requests.post(
        f"{_BASE}/me/events",
        headers=_headers(),
        data=json.dumps(event_data),
    )
    _raise_for_status(response)
    return response.json()


def check_conflicts(start: str, end: str) -> bool:
    """
    GET /me/calendarView for the given time range.
    Returns True if one or more events already exist in that slot, False otherwise.
    start / end must be ISO 8601 strings, e.g. '2026-05-28T10:00:00Z'.
    """
    params = {
        "startDateTime": start,
        "endDateTime": end,
        "$top": 1,
        "$select": "id,subject,start,end",
    }
    response = requests.get(f"{_BASE}/me/calendarView", headers=_headers(), params=params)
    _raise_for_status(response)
    events = response.json().get("value", [])
    return len(events) > 0


if __name__ == "__main__":
    import pprint
    print("=== Calendars ===")
    pprint.pprint(get_calendars())
    print("\n=== Upcoming Events (7 days) ===")
    pprint.pprint(get_upcoming_events(days=7))
