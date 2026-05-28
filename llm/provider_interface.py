"""
Abstract base for any LLM provider integration.
"""
from abc import ABC, abstractmethod
from models.email_models import LLMContext

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, context: LLMContext) -> dict:
        """
        Given an LLMContext object, returns a dictionary with
        'draft' (str), 'summary' (str, optional), and 'reasoning' (str, optional)
        """
        pass
