# llm

This module handles all LLM interactions. It defines a provider abstraction, two concrete provider implementations (OpenAI and Google Gemini), and a prompt builder that converts an `LLMContext` into a formatted string prompt.

## Files

| File | Purpose |
|---|---|
| `provider_interface.py` | Abstract base class `LLMProvider` with a single `generate(context)` method. All providers must implement this interface. |
| `openai_provider.py` | `OpenAIProvider` - calls the OpenAI Chat Completions API using GPT-3.5-turbo by default. Also exposes `generate_from_prompt(prompt)` for raw string prompts used by the LLM classifier. |
| `gemini_provider.py` | `GeminiProvider` - calls the Google Gemini API using `gemini-2.0-flash`. Uses the `google-genai` v2 client. |
| `prompt_builder.py` | `build_prompt(context)` - formats an `LLMContext` object into the structured string prompt sent to the LLM. |
| `__init__.py` | Package init. |

## Provider Selection

The active provider is selected in `pipeline/orchestrator.py` at import time based on the `LLM_PROVIDER` environment variable:

- `LLM_PROVIDER=gemini` loads `GeminiProvider`
- `LLM_PROVIDER=openai` (or any other value) loads `OpenAIProvider`

## Prompt Format

`build_prompt` produces a prompt structured as:

```
Email from: <sender>
Subject: <subject>
Text:
<cleaned_body>

---
Classification:
 - Safety: <safety>
 - Source: <source>
 - Intent: <intent>
 - Priority: <priority>
Action: <action>
Instructions:
<reply_objective>
Tone: <tone_guidance>
---
## Please produce only the draft email body below this line.##
```

## Return Value

All providers return a dict with three keys:

```python
{
    "draft": "...",      # The generated email body
    "summary": "...",    # Optional summary (blank for current providers)
    "reasoning": "..."   # Explanation of what was done
}
```

## Adding a New Provider

1. Create a new file, e.g., `claude_provider.py`.
2. Subclass `LLMProvider` and implement `generate(context: LLMContext) -> dict`.
3. Update the provider selection logic in `pipeline/orchestrator.py`.
4. Add any required API keys to `.env` and `config/settings.py`.
