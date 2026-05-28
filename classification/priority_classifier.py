"""
PriorityClassifier: Assigns email priority
"""
import re
from models.email_models import CleanedEmail
from utils.constants import PRIORITY_LABELS

class PriorityClassifier:
    high_priority_phrases = ["urgent", "asap", "immediate", "critical", "important", "action required", "need clarification"]
    low_priority_keywords = ["fyi", "no action required", "newsletter"]

    def classify(self, email: CleanedEmail) -> str:
        subj_body = f"{email.subject.lower()} {email.cleaned_body.lower()}"
        if any(kw in subj_body for kw in self.high_priority_phrases):
            return "high"
        if any(kw in subj_body for kw in self.low_priority_keywords):
            return "low"
        return "medium"
