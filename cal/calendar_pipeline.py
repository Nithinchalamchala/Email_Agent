"""
Orchestrates the end-to-end calendar processing flow: receives a cleaned email,
runs extractor to identify calendar intent, builds LLM context via prompt_builder,
calls the LLM for structured event data, then dispatches the appropriate action
via actions.py. Returns a CalendarPipelineOutput.
"""
import pprint
from datetime import datetime

from cal.extractor import extract_calendar_details
from cal.actions import execute_action
from cal.models import CalendarEvent, CalendarPipelineOutput


def run_calendar_pipeline(cleaned_email: dict, token: str | None = None) -> dict:
    """
    Entry point for calendar processing.

    Args:
        cleaned_email: dict with keys sender, subject, cleaned_body (or body), timestamp

    Returns:
        CalendarPipelineOutput serialised as dict
    """
    # Step 1 — extract event details via LLM
    extracted = extract_calendar_details(cleaned_email)

    # Step 2 — execute the appropriate Graph API action
    action_result = execute_action(extracted, token=token)

    # Step 3 — assemble structured output
    event = None
    if (
        action_result["action"] == "event_created"
        and extracted.get("start_time")
        and extracted.get("end_time")
    ):
        try:
            event = CalendarEvent(
                subject=extracted.get("title", ""),
                start=datetime.fromisoformat(extracted["start_time"]),
                end=datetime.fromisoformat(extracted["end_time"]),
                location=extracted.get("location"),
                body=extracted.get("description", ""),
                attendees=extracted.get("attendees", []),
                event_id=action_result.get("details", {}).get("id"),
            )
        except (ValueError, TypeError):
            pass  # malformed datetime strings — leave event as None

    details = action_result.get("details")
    reasoning = (
        details.get("reason", "")
        if isinstance(details, dict) and "reason" in details
        else ""
    )

    output = CalendarPipelineOutput(
        action=action_result["action"],
        status=action_result["status"],
        extracted_event=extracted,
        details=details,
        event=event,
        reasoning=reasoning,
        success=action_result["status"] == "success",
        graph_response=details if action_result["action"] == "event_created" else None,
        requires_human_review=action_result["action"] == "conflict_detected",
    )

    return output.model_dump()


if __name__ == "__main__":
    sample_email = {
        "sender": "vpj162@gmail.com",
        "subject": "Q2 Report Discussion",
        "cleaned_body": (
            "Hi, can we meet on June 2nd at 11am IST for 1 hour to discuss the Q2 report? "
            "My office, Bangalore. Please confirm."
        ),
        "timestamp": "2026-05-28T10:00:00",
    }

    result = run_calendar_pipeline(sample_email)
    pprint.pprint(result)
