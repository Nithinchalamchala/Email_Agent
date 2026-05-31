"""
Extracts calendar-relevant entities (dates, times, durations, attendees, meeting topics)
from cleaned email text. Returns structured data consumed by calendar_pipeline.py.
"""
import json
import re
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from config.settings import settings

# All times from the LLM are treated as IST; Python converts to UTC reliably
_USER_TZ = ZoneInfo("Asia/Kolkata")  # IST = UTC+5:30


def _local_to_utc(dt_str: str | None) -> str | None:
    """Convert a naive IST datetime string to a UTC ISO string."""
    if not dt_str:
        return None
    try:
        local_dt = datetime.fromisoformat(dt_str).replace(tzinfo=_USER_TZ)
        utc_dt = local_dt.astimezone(timezone.utc)
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        return dt_str  # return as-is if parsing fails

_SYSTEM_PROMPT = """\
You are a calendar extraction assistant. Given an email, extract meeting details and return ONLY a valid JSON object — no markdown, no code fences, no explanation.

JSON schema:
{
  "title":       "<string: meeting title or subject>",
  "date":        "<ISO date string YYYY-MM-DD, or null if not found>",
  "start_time":  "<ISO datetime string YYYY-MM-DDTHH:MM:SS in IST, or null if not found>",
  "end_time":    "<ISO datetime string YYYY-MM-DDTHH:MM:SS in IST, or null if not found>",
  "location":    "<string or null>",
  "attendees":   ["<email address>", ...],
  "description": "<string: brief summary of meeting purpose>",
  "confidence":  <float 0.0-1.0: how confident this email is a real meeting request>
}

Rules:
- Resolve relative dates (e.g. "tomorrow", "next Monday") using the email timestamp provided.
- Return start_time and end_time in IST (India Standard Time) — do NOT convert to UTC.
- If the email mentions a timezone (e.g. "3pm IST", "2pm UTC+5:30"), keep the time as stated — just return the clock value in IST.
- If the email says "3pm UTC" or "3pm GMT", convert to IST by adding 5 hours 30 minutes, then return that IST time.
- If no timezone is mentioned, assume IST.
- If no explicit end time, infer from duration mentioned ("1 hour meeting" → end = start + 1h).
- Include sender email in attendees if this looks like an invite.
- Set confidence < 0.5 if the email is not clearly a meeting request.
- Return null for any field that cannot be determined.
"""

_USER_TEMPLATE = """\
Email timestamp: {timestamp}
From: {sender}
Subject: {subject}
Body:
{body}
"""


def _call_gemini(prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()


def _call_openai(prompt: str) -> str:
    import openai
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=400,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


def _parse_json(raw: str) -> dict:
    """Strip markdown fences if present, then parse JSON."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return json.loads(cleaned)


def extract_calendar_details(email: dict[str, Any]) -> dict[str, Any]:
    """
    Takes a cleaned email dict with keys: sender, subject, cleaned_body, timestamp.
    Returns a dict with: title, date, start_time, end_time, location,
    attendees, description, confidence.
    """
    user_message = _USER_TEMPLATE.format(
        timestamp=email.get("timestamp", "unknown"),
        sender=email.get("sender", ""),
        subject=email.get("subject", ""),
        body=email.get("cleaned_body", email.get("body", "")),
    )

    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini":
        # Gemini: combine system + user into one prompt
        raw = _call_gemini(_SYSTEM_PROMPT + "\n\n" + user_message)
    else:
        raw = _call_openai(user_message)

    try:
        result = _parse_json(raw)
    except json.JSONDecodeError:
        result = {
            "title": email.get("subject", ""),
            "date": None,
            "start_time": None,
            "end_time": None,
            "location": None,
            "attendees": [],
            "description": "",
            "confidence": 0.0,
        }

    result.setdefault("confidence", 0.0)

    # Convert IST times to UTC reliably in Python (not via LLM)
    result["start_time"] = _local_to_utc(result.get("start_time"))
    result["end_time"]   = _local_to_utc(result.get("end_time"))

    return result


if __name__ == "__main__":
    import pprint

    sample_email = {
        "sender": "rahul.sharma@example.com",
        "subject": "Q2 Report Discussion",
        "cleaned_body": (
            "Hi, can we meet tomorrow at 3pm IST for 1 hour to discuss the Q2 report? "
            "My office, Bangalore. Please confirm."
        ),
        "timestamp": "2026-05-28T10:00:00",
    }

    print(f"LLM provider: {settings.LLM_PROVIDER}")
    result = extract_calendar_details(sample_email)
    pprint.pprint(result)
