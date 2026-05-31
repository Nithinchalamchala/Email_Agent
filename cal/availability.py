"""
Queries the user's calendar and formats a readable free/busy context string
for injection into LLM prompts. Used by smart_reply.py.
"""
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from cal.graph_client import get_upcoming_events


def get_calendar_context(days: int = 7, token: str | None = None) -> str:
    """
    Returns a plain-text summary of the user's calendar for the next `days` days,
    suitable for pasting into an LLM prompt.

    Example output:
        Your calendar for the next 7 days (UTC):
        • Sat May 30: Q2 Report 09:30, Project Meeting 16:30
        • Sun May 31: Free
        • Mon Jun 01: Free
        ...
    """
    try:
        data = get_upcoming_events(days=days, token=token)
        events = data.get("value", [])
    except Exception as e:
        return f"(Calendar context unavailable: {e})"

    # Group events by ISO date string
    by_date: dict[str, list[str]] = defaultdict(list)
    for ev in events:
        start_str = (ev.get("start") or {}).get("dateTime", "")
        if not start_str:
            continue
        try:
            dt = datetime.fromisoformat(start_str.rstrip("Z")).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        date_key = dt.date().isoformat()
        time_label = dt.strftime("%H:%M")
        subject = ev.get("subject") or "Busy"
        by_date[date_key].append(f"{time_label} {subject}")

    now = datetime.now(timezone.utc)
    lines = ["Your calendar for the next 7 days (times in UTC):"]
    for i in range(days):
        day = (now + timedelta(days=i)).date()
        key = day.isoformat()
        # Short readable label e.g. "Sat May 30"
        label = day.strftime("%a %b ") + str(day.day)
        if key in by_date:
            lines.append(f"• {label}: {', '.join(by_date[key])}")
        else:
            lines.append(f"• {label}: Free")

    return "\n".join(lines)
