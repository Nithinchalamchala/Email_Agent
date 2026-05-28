"""
LLMProvider implementation for Google Gemini API using google-genai v2.x
"""

from google import genai
from typing import Dict

from config.settings import settings
from models.email_models import LLMContext
from .provider_interface import LLMProvider
from .prompt_builder import build_prompt
from utils.logger import logger


class GeminiProvider(LLMProvider):

    def __init__(self, api_key=None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        print("API KEY:", self.api_key)
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, context: LLMContext) -> Dict:
        prompt = build_prompt(context)

        logger.info("Sending prompt to Gemini LLM provider.")

        try:
            response = self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                        )

            draft = ""

            if hasattr(response, "text") and response.text:
                draft = response.text.strip()

            return {
                "draft": draft,
                "summary": "",
                "reasoning": "Draft generated via Gemini."
            }

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")

            return {
                "draft": "",
                "summary": "",
                "reasoning": f"LLM error: {e}"
            }