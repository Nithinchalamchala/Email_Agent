# models

This module defines all Pydantic data models used across the Hermes pipeline. Every stage in the pipeline exchanges strongly typed, validated objects defined here.

## Files

| File | Purpose |
|---|---|
| `email_models.py` | All pipeline data models. |
| `__init__.py` | Package init. |

## Models

### RawEmail

The unprocessed email as it arrives from the email source (O365, sample file, etc.).

| Field | Type | Description |
|---|---|---|
| `sender` | str | Sender email address |
| `subject` | str | Email subject line |
| `body` | str | Raw email body (may contain HTML) |
| `timestamp` | str | ISO 8601 received timestamp |
| `thread_id` | str | Conversation/thread ID |
| `metadata` | dict | Provider-specific metadata (message ID, internet message ID, etc.) |

### CleanedEmail

Produced by the preprocessing module. Identical to `RawEmail` except `body` is replaced by `cleaned_body`.

| Field | Type | Description |
|---|---|---|
| `cleaned_body` | str | HTML-stripped, signature-removed, whitespace-normalized body text |

All other fields are the same as `RawEmail`.

### ClassificationResult

Holds the output of all four classifiers.

| Field | Type | Values |
|---|---|---|
| `safety` | str | `spam`, `suspicious`, `safe` |
| `source` | str | `customer_external`, `internal`, `broadcast_newsletter`, `automated_system`, `unknown` |
| `intent` | str | `reply_needed`, `informational`, `meeting_related`, `complaint`, `support_request`, `follow_up` |
| `priority` | str | `high`, `medium`, `low` |

### WorkflowAction

The decision produced by the decision engine.

| Field | Type | Description |
|---|---|---|
| `action` | str | One of the workflow action constants |
| `requires_human_review` | bool | Whether a human should review the output |
| `reasoning` | str | Human-readable explanation of why this action was chosen |

### LLMContext

The complete context packet passed to the LLM provider.

| Field | Type | Description |
|---|---|---|
| `sender` | str | Sender email address |
| `subject` | str | Email subject |
| `cleaned_body` | str | Preprocessed email body |
| `classification` | ClassificationResult | All four classification labels |
| `action` | WorkflowAction | Chosen workflow action |
| `reply_objective` | str | Plain-English LLM instruction derived from the action |
| `tone_guidance` | str | Tone instruction for the LLM |

### PipelineOutput

The final structured result returned by the pipeline.

| Field | Type | Description |
|---|---|---|
| `classification` | ClassificationResult | All four labels |
| `action` | str | Chosen workflow action name |
| `draft` | str (optional) | Generated reply draft |
| `summary` | str (optional) | Generated summary |
| `reasoning` | str (optional) | Action or LLM reasoning |
| `requires_human_review` | bool | Human review flag |
