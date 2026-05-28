# Hermes Email Intelligence Pipeline

Hermes is a modular, production-grade Python system that automatically processes, classifies, and generates draft replies for incoming emails. It connects to Microsoft 365 via the Microsoft Graph API, runs each email through a multi-stage classification pipeline, and uses an LLM (OpenAI or Google Gemini) to produce a contextual draft response.

## How It Works

A raw email enters the pipeline and passes through five sequential stages:

1. **Preprocessing** - HTML is stripped, email signatures are removed, and whitespace is normalized.
2. **Classification** - Four independent classifiers assign safety, source, intent, and priority labels.
3. **Decision Engine** - A rule table maps the classification result to a workflow action (draft, summarize, ignore).
4. **Context Building** - A structured LLM context object is assembled with the cleaned email and all labels.
5. **LLM Generation** - The configured provider (OpenAI GPT or Gemini) generates a draft reply or summary.

## Project Structure

```
hermes_email_agent/
├── main.py                  Entry point for single-email processing (CLI)
├── fetch_unread_o365.py     Fetches unread emails from Office 365 and runs the full pipeline
├── batch_test.py            Runs the pipeline against the sample_data/batch test fixtures
├── config.py                Legacy config shim (superseded by config/)
├── requirements.txt         Python dependencies
├── .env.example             Environment variable template
│
├── pipeline/                Pipeline orchestrator that wires all stages together
├── preprocessing/           Email cleaning: HTML removal, signature stripping, whitespace normalization
├── classification/          Four classifiers: safety, source, intent, priority
├── decision_engine/         Rule table that maps classification -> workflow action
├── context/                 Assembles LLMContext from cleaned email + classification + action
├── llm/                     LLM provider abstraction (OpenAI, Gemini) and prompt builder
├── models/                  Pydantic data models used across the pipeline
├── config/                  Centralized settings loaded from environment variables
├── utils/                   Shared utilities: logger, helpers, constants
│
├── dashboard/               FastAPI backend + React frontend for visualizing batch results
├── sample_data/             Sample emails and expected outputs for development and testing
│
├── agent/                   Reserved for future agentic loop and autonomous decision logic
├── storage/                 Reserved for future persistent storage and result archiving
├── prompts/                 Reserved for externalized prompt templates
├── notifications/           Reserved for future notification dispatch (email, Slack, Telegram)
├── outlook/                 Reserved for additional Outlook/O365 integration utilities
└── logs/                    Runtime log output directory
```

## Quick Start

```bash
# 1. Copy the environment template and fill in your keys
cp .env.example .env

# 2. Install dependencies (use a virtual environment)
pip install -r requirements.txt

# 3. Run the pipeline against a single email file
python main.py sample_data/sample_email.json

# 4. Run the pipeline against all batch test fixtures
python batch_test.py

# 5. Fetch unread emails from Office 365 and process them
python fetch_unread_o365.py
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | If using OpenAI | OpenAI API key |
| `GEMINI_API_KEY` | If using Gemini | Google Gemini API key |
| `LLM_PROVIDER` | Yes | `openai` or `gemini` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO`, `WARNING` (default: `INFO`) |
| `MS_GRAPH_TOKEN` | For O365 fetch | Microsoft Graph API bearer token |

## LLM Provider Selection

Set `LLM_PROVIDER=gemini` in `.env` to use Google Gemini 2.0 Flash. Set `LLM_PROVIDER=openai` to use GPT-3.5-turbo. Both providers implement the same `LLMProvider` interface defined in `llm/provider_interface.py`, so adding a new provider requires only a single new class.

## Dashboard

A FastAPI + React dashboard is available to review batch-processed results. See [dashboard/README.md](dashboard/README.md) for startup instructions.

## Module Documentation

Each subdirectory contains a README explaining the purpose of that module, the files inside it, and how it fits into the pipeline.
