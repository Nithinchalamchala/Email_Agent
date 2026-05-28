"""
SourceClassifier: Identifies sender type
"""
from models.email_models import CleanedEmail
from utils.helpers import extract_email_domain
from utils.constants import SOURCE_LABELS

class SourceClassifier:
    known_internal_domains = ["lumiq.ai", "lumiaq.com"]  # Extend this list as needed

    def classify(self, email: CleanedEmail) -> str:
        domain = extract_email_domain(email.sender)
        if domain in self.known_internal_domains:
            return "internal"
        if "newsletter" in email.subject.lower() or "unsubscribe" in email.cleaned_body.lower():
            return "broadcast_newsletter"
        if "noreply" in email.sender or "no-reply" in email.sender:
            return "automated_system"
        if not domain:
            return "unknown"
        return "customer_external"
