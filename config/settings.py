from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()  # Read .env file

class Settings:
    """Central settings management for the application. Extend as needed."""
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SIGNATURE_PATTERNS: list = [
        "--", "Regards,", "Best,", "Thanks,", "Sincerely,", "Cheers,"
    ]
    # Add more config entries as needed

settings = Settings()
