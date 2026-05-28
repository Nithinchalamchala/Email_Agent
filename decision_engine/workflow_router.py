"""
WorkflowRouter: Maps any email that isn't spam to draft-and-notify by default, for safer pipeline coverage.
"""

from typing import Tuple
from models.email_models import ClassificationResult, WorkflowAction
from utils.constants import WORKFLOW_ACTIONS

# Updated rule table: All non-spam cases now trigger generate_draft_and_notify (always-on)
RULES = [
    # Spam: always ignore
    (("spam", None, None, None), "ignore", False, "Email marked as spam."),

    # Newsletters: summarize only
    ((None, "broadcast_newsletter", None, None), "summarize_only", False, "Email is a newsletter."),

    # Everything else: now triggers draft + notify
    ((None, None, None, None), "generate_draft_and_notify", True, "Default: action+draft for all non-spam emails."),
]

def matches(rule: Tuple, result: ClassificationResult):
    """Determines if a rule matches a classification."""
    # None = wildcard
    return all(
        r is None or getattr(result, name) == r
        for r, name in zip(rule, ['safety', 'source', 'intent', 'priority'])
    )

def route_workflow(classification: ClassificationResult) -> WorkflowAction:
    for (rule, action, needs_review, reasoning) in RULES:
        if matches(rule, classification):
            return WorkflowAction(
                action=action,
                requires_human_review=needs_review,
                reasoning=reasoning
            )
    # Should not reach here due to fallback
    return WorkflowAction(
        action="generate_draft_and_notify",
        requires_human_review=True,
        reasoning="All non-spam emails now default to draft + notify."
    )
