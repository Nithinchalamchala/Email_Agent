import re
from typing import Optional

def extract_email_domain(email: str) -> Optional[str]:
    """Extracts domain from email address."""
    if '@' in email:
        return email.split('@')[-1].lower()
    return None

def is_external_email(domain: str, internal_domains: list) -> bool:
    """Checks if domain is external."""
    return domain not in internal_domains
