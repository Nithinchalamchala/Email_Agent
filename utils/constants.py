# /Users/nithin/Desktop/LUMIQ_AI/hermes_email_agent/utils/constants.py

SAFETY_LABELS = ["spam", "suspicious", "safe"]
SOURCE_LABELS = ["customer_external", "internal", "broadcast_newsletter", "automated_system", "unknown"]
INTENT_LABELS = ["reply_needed", "informational", "meeting_related", "complaint", "support_request", "follow_up"]
PRIORITY_LABELS = ["high", "medium", "low"]
WORKFLOW_ACTIONS = [
    "ignore", "summarize_only", "generate_draft_and_notify", "notify_only", "generate_draft"
]
