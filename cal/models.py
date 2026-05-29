from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class CalendarEvent(BaseModel):
    subject: str
    start: datetime
    end: datetime
    location: Optional[str] = None
    body: Optional[str] = None
    attendees: List[str] = []
    is_all_day: bool = False
    organizer: Optional[str] = None
    event_id: Optional[str] = None  # Graph API event ID, set after creation


class CalendarPipelineOutput(BaseModel):
    action: str                               # event_created | conflict_detected | no_action
    status: str                               # success | conflict | skipped | error
    extracted_event: Optional[dict] = None    # raw extractor output
    details: Optional[Any] = None             # Graph API response or conflict/skip reason
    event: Optional[CalendarEvent] = None     # structured event (set on event_created)
    reasoning: str = ""
    success: Optional[bool] = None
    graph_response: Optional[dict] = None
    requires_human_review: bool = False
