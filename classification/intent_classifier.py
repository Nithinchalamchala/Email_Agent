"""
IntentClassifier: Determines primary intent of the email
"""
import re
from models.email_models import CleanedEmail
from utils.constants import INTENT_LABELS

class IntentClassifier:
    intent_rules = [
        ("meeting_related", lambda e: "meeting" in e.subject.lower() or "calendar invite" in e.cleaned_body.lower()),
        ("complaint", lambda e: "not happy" in e.cleaned_body.lower() or "complaint" in e.subject.lower() or "issue" in e.cleaned_body.lower()),
        ("support_request", lambda e: "support" in e.subject.lower() or "help" in e.cleaned_body.lower()),
        ("follow_up", lambda e: "following up" in e.cleaned_body.lower() or "follow up" in e.subject.lower()),
        ("reply_needed", lambda e: bool(re.search(r'\\bplease reply\\b|\\bkindly respond\\b', e.cleaned_body.lower())) or "?" in e.cleaned_body),
        ("informational", lambda e: True)  # fallback
    ]

    def classify(self, email: CleanedEmail) -> str:
        for label, rule in self.intent_rules:
            if rule(email):
                return label
        return "informational"
