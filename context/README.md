# context

This module assembles the `LLMContext` object that is passed to the LLM provider for draft or summary generation.

## Files

| File | Purpose |
|---|---|
| `context_builder.py` | `build_llm_context(cleaned_email, classification, action)` function that constructs and returns an `LLMContext`. |
| `__init__.py` | Package init. |

## What Gets Packed Into LLMContext

The `LLMContext` Pydantic model contains:

| Field | Source |
|---|---|
| `sender` | `CleanedEmail.sender` |
| `subject` | `CleanedEmail.subject` |
| `cleaned_body` | `CleanedEmail.cleaned_body` |
| `classification` | `ClassificationResult` (safety, source, intent, priority labels) |
| `action` | `WorkflowAction` (action name, reasoning, requires_human_review) |
| `reply_objective` | Derived from the action type - a plain-English instruction for the LLM |
| `tone_guidance` | Fixed tone instruction ("professional, courteous, and concise") |

## Reply Objective Mapping

The `reply_objective` field is set based on the workflow action:

| Action | Objective sent to LLM |
|---|---|
| `generate_draft` | Draft a professional and concise email reply. |
| `generate_draft_and_notify` | Draft a high-priority reply and flag for human approval. |
| `summarize_only` | Summarize the email for user review, no reply needed. |
| `notify_only` | No reply required; prepare notification for the user. |
| `ignore` | No action required. |

## Extending Context

To enrich the prompt with more context:

- Add a RAG retrieval step before calling `build_llm_context` and include retrieved documents in a new `LLMContext` field.
- Add sender history (e.g., previous thread summaries) to give the LLM conversational awareness.
- Include company-specific policy snippets to guide tone and content.

The `LLMContext` model lives in `models/email_models.py`. Add new fields there and populate them in `context_builder.py`.
