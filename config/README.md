# config

This module provides centralized, environment-driven configuration for the entire application. All settings are read from environment variables (loaded from `.env` via `python-dotenv`).

## Files

| File | Purpose |
|---|---|
| `settings.py` | `Settings` class that reads all environment variables. A singleton `settings` instance is imported everywhere in the codebase. |
| `logging_config.py` | `setup_logger(name)` factory function that creates a named `logging.Logger` with a consistent format. |
| `__init__.py` | Package init. |

## Settings Reference

| Setting | Environment Variable | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | `OPENAI_API_KEY` | None | OpenAI API key. Required when `LLM_PROVIDER=openai`. |
| `GEMINI_API_KEY` | `GEMINI_API_KEY` | None | Google Gemini API key. Required when `LLM_PROVIDER=gemini`. |
| `LLM_PROVIDER` | `LLM_PROVIDER` | `openai` | Which LLM provider to use: `openai` or `gemini`. |
| `LOG_LEVEL` | `LOG_LEVEL` | `INFO` | Python logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `SIGNATURE_PATTERNS` | (hardcoded) | see settings.py | List of strings that mark the start of an email signature. |

## Logger Format

All loggers produced by `setup_logger` share the same format:

```
[2025-01-01 12:00:00,000] [INFO] module_name: message
```

## How to Add a New Setting

1. Add a new class attribute to `Settings` in `settings.py`, reading from `os.getenv`.
2. Set a sensible default so the application runs without that variable when it is optional.
3. Add the variable to `.env.example` with a comment.
4. Document it in this README.
