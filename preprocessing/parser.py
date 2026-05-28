"""
Parser: Composes cleaned email models for the pipeline
"""

from models.email_models import RawEmail, CleanedEmail
from utils.logger import logger
from .cleaner import EmailCleaner

def preprocess_email(raw_email: RawEmail) -> CleanedEmail:
    """
    Cleans raw email text and returns a CleanedEmail dataclass
    """
    cleaner = EmailCleaner()
    cleaned_body = cleaner.clean(raw_email.body)
    logger.info(f"Preprocessed email from '{raw_email.sender}' - subject: '{raw_email.subject}'")
    return CleanedEmail(
        sender=raw_email.sender,
        subject=raw_email.subject,
        cleaned_body=cleaned_body,
        timestamp=raw_email.timestamp,
        thread_id=raw_email.thread_id,
        metadata=raw_email.metadata
    )
