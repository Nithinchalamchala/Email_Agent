"""
LLM Prompt Builder
"""
from models.email_models import LLMContext

def build_prompt(context: LLMContext) -> str:
    return (
        f"Email from: {context.sender}\n"
        f"Subject: {context.subject}\n"
        f"Text:\n{context.cleaned_body}\n\n"
        f"---\n"
        f"Classification:\n"
        f" - Safety: {context.classification.safety}\n"
        f" - Source: {context.classification.source}\n"
        f" - Intent: {context.classification.intent}\n"
        f" - Priority: {context.classification.priority}\n"
        f"Action: {context.action.action}\n"
        f"Instructions:\n{context.reply_objective}\n"
        f"Tone: {context.tone_guidance}\n"
        f"---\n"
        f"## Please produce only the draft email body below this line.##\n"
    )
