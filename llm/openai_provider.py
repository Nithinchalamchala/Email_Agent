import openai
from typing import Dict
from config.settings import settings
from models.email_models import LLMContext
from .provider_interface import LLMProvider
from .prompt_builder import build_prompt
from utils.logger import logger

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model_name or "gpt-3.5-turbo"

    def generate(self, context: LLMContext) -> Dict:
        prompt = build_prompt(context)
        logger.info("Sending prompt to OpenAI LLM provider.")
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert professional assistant that drafts concise, polite high-quality enterprise emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            draft = response.choices[0].message.content.strip()
            return {"draft": draft, "summary": "", "reasoning": "Draft generated via OpenAI."}
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return {"draft": "", "summary": "", "reasoning": f"LLM error: {e}"}

    def generate_from_prompt(self, prompt: str) -> Dict:
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=100,
            )
            content = response.choices[0].message.content.strip()
            return {"draft": content}
        except Exception as e:
            logger.error(f"OpenAI LLM direct prompt failed: {e}")
            return {"draft": ""}
