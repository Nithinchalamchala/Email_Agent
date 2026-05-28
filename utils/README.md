# utils

Shared utility code used by multiple modules across the pipeline. Nothing in this directory is specific to any one pipeline stage.

## Files

| File | Purpose |
|---|---|
| `constants.py` | All valid label value lists for the four classifiers and all workflow action names. Imported by classifiers and the decision engine. |
| `helpers.py` | General-purpose helper functions. |
| `logger.py` | Module-level logger instance (`logger`) that is imported directly wherever logging is needed. |
| `__init__.py` | Package init. |

## Constants

`constants.py` defines five lists:

```python
SAFETY_LABELS   = ["spam", "suspicious", "safe"]
SOURCE_LABELS   = ["customer_external", "internal", "broadcast_newsletter", "automated_system", "unknown"]
INTENT_LABELS   = ["reply_needed", "informational", "meeting_related", "complaint", "support_request", "follow_up"]
PRIORITY_LABELS = ["high", "medium", "low"]
WORKFLOW_ACTIONS = ["ignore", "summarize_only", "generate_draft_and_notify", "notify_only", "generate_draft"]
```

When adding a new label to a classifier, add it here first so it is visible to the LLM classifier prompt and any validation logic.

## Helpers

`helpers.py` currently provides:

- `extract_email_domain(email: str) -> Optional[str]` - Splits an email address on `@` and returns the domain portion in lowercase. Returns `None` if no `@` is found.
- `is_external_email(domain: str, internal_domains: list) -> bool` - Returns `True` if the domain is not in the provided internal domains list.

## Logger

`logger.py` exposes a single pre-configured logger named `hermes`:

```python
from utils.logger import logger
logger.info("message")
```

The log level is controlled by the `LOG_LEVEL` environment variable (default: `INFO`). Format: `[timestamp] [LEVEL] module: message`.
