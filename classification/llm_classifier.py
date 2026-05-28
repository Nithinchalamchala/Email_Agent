from llm.provider_interface import LLMProvider
from models.email_models import CleanedEmail
from config.settings import settings
from .intent_classifier import INTENT_LABELS
from .source_classifier import SOURCE_LABELS
from utils.logger import logger
import json
import re

class LLMIntentSourceClassifier:
    """
    LLM-based classifier for ambiguous or complex intent and source situations.
    """
    def __init__(self, provider_cls=None):
        # Default: use current OpenAIProvider (other providers pluggable)
        if not provider_cls:
            from llm.openai_provider import OpenAIProvider
            provider_cls = OpenAIProvider
        self.provider = provider_cls()

    def classify(self, cleaned_email: CleanedEmail) -> dict:
        prompt = (
            "Classify this email.\n"
            "Options for intent: " + ", ".join(INTENT_LABELS) + "\n"
            "Options for source: " + ", ".join(SOURCE_LABELS) + "\n"
            "Respond ONLY with a JSON object in this format (no commentary):\n"
            '{"source": "...", "intent": "..."}'
            "\nEmail content:\n"
            f"From: {cleaned_email.sender}\nSubject: {cleaned_email.subject}\nBody: {cleaned_email.cleaned_body}\n"
        )
        logger.info("Invoking LLM for ambiguous classification on email.")
        try:
            result = self.provider.generate_from_prompt(prompt)
            match = re.search(r'{.*}', result.get('draft', ''))
            llm_json = json.loads(match.group()) if match else {}
            return {
                "source": llm_json.get("source"),
                "intent": llm_json.get("intent"),
                "llm_raw": result.get("draft")
            }
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return {}
