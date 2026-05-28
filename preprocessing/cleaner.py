"""
Cleaner: Email text normalization and preprocessing utilities
"""

import re
from typing import Tuple
from config.settings import settings
from utils.logger import logger

class EmailCleaner:
    """Cleans and normalizes email content."""

    def __init__(self, signature_patterns: list = None):
        self.signature_patterns = signature_patterns or settings.SIGNATURE_PATTERNS

    def remove_html(self, text: str) -> str:
        """Removes basic HTML tags. Extendable for more robust stripping."""
        cleanr = re.compile('<.*?>')
        return re.sub(cleanr, '', text)

    def remove_signature(self, text: str) -> Tuple[str, str]:
        """Removes signature using simple patterns. Returns (body, signature)."""
        for sig in self.signature_patterns:
            idx = text.lower().find(sig.lower())
            if idx != -1:
                logger.debug(f"Signature detected: {sig!r}")
                return text[:idx].strip(), text[idx:].strip()
        return text.strip(), ""

    def normalize_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def clean(self, text: str) -> str:
        # Remove HTML, signature, normalize
        text = self.remove_html(text)
        body, _ = self.remove_signature(text)
        return self.normalize_whitespace(body)
