"""
Generates an availability-aware draft reply by injecting the user's real calendar
context into the LLM prompt. Zero changes to the main email pipeline.
"""
from config.settings import settings
from cal.availability import get_calendar_context

_PROMPT_TEMPLATE = """\
You are a professional email assistant for {user}.
Generate a concise, helpful reply to the email below using the calendar context provided.

--- INCOMING EMAIL ---
From: {sender}
Subject: {subject}
{body}
---------------------

{calendar_context}

Instructions:
- If the email asks about availability or proposes a meeting time, use the calendar to give a specific, accurate answer
- If the proposed time is already busy, suggest 2-3 genuinely free slots from the calendar
- If the proposed time is free, confirm it works
- If the email is not about scheduling, write a normal helpful reply (ignore calendar context)
- Keep the reply professional and under 150 words
- Write only the reply body, no subject line, no sign-off placeholder
"""


def _call_openai(prompt: str) -> str:
    import openai
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text.strip()


def generate_smart_reply(email: dict, token: str | None = None) -> dict:
    """
    Args:
        email: dict with keys sender, subject, body (or original_body)
        token: MSAL bearer token for Graph API calendar access

    Returns:
        { draft, calendar_context, calendar_checked }
    """
    calendar_context = get_calendar_context(days=7, token=token)

    sender  = email.get("sender", "the sender")
    subject = email.get("subject", "")
    body    = email.get("body") or email.get("original_body") or email.get("cleaned_body", "")

    prompt = _PROMPT_TEMPLATE.format(
        user=settings.GRAPH_USER_EMAIL if hasattr(settings, "GRAPH_USER_EMAIL") else "the user",
        sender=sender,
        subject=subject,
        body=body,
        calendar_context=calendar_context,
    )

    provider = settings.LLM_PROVIDER.lower()
    try:
        draft = _call_gemini(prompt) if provider == "gemini" else _call_openai(prompt)
    except Exception as e:
        draft = f"(Smart reply generation failed: {e})"

    return {
        "draft": draft,
        "calendar_context": calendar_context,
        "calendar_checked": True,
    }
