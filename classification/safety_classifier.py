"""
SafetyClassifier: Detects spam/suspicious/safe
"""
import re
from models.email_models import CleanedEmail
from utils.constants import SAFETY_LABELS

class SafetyClassifier:
    """
    Classifies emails into 'spam', 'suspicious', or 'safe'.
    """

    spam_keywords = ['free money', 'win big', 'prize', 'lottery', 'urgent assistance']
    suspicious_patterns = [r'\b(?:account|password|verify|click here|reset)\b']

    def classify(self, email: CleanedEmail) -> str:
        text = email.cleaned_body.lower()
        if any(word in text for word in self.spam_keywords):
            return 'spam'
        if any(re.search(pat, text) for pat in self.suspicious_patterns):
            return 'suspicious'
        return 'safe'
