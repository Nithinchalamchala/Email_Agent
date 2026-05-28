"""
Context builder: Packages context for LLM prompting.
"""

from models.email_models import CleanedEmail, ClassificationResult, WorkflowAction, LLMContext

def build_llm_context(
    cleaned_email: CleanedEmail,
    classification: ClassificationResult,
    action: WorkflowAction
) -> LLMContext:
    reply_objective = {
        "generate_draft": "Draft a professional and concise email reply that addresses the user's query.",
        "generate_draft_and_notify": "Draft a high-priority reply and flag for human approval.",
        "summarize_only": "Summarize the email for user reviewno reply needed.",
        "notify_only": "No reply required; prepare notification for the user.",
        "ignore": "No action required."
    }.get(action.action, "Prepare appropriate response.")

    tone_guidance = "Use a professional, courteous, and concise tone."

    return LLMContext(
        sender=cleaned_email.sender,
        cleaned_body=cleaned_email.cleaned_body,
        subject=cleaned_email.subject,
        classification=classification,
        action=action,
        reply_objective=reply_objective,
        tone_guidance=tone_guidance
    )
