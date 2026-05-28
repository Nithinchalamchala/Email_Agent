# classification

This module contains all email classifiers. Each classifier receives a `CleanedEmail` object and returns a single label string. The four classifiers run independently in the pipeline and their outputs are combined into a `ClassificationResult`.

## Files

| File | Purpose |
|---|---|
| `safety_classifier.py` | Detects spam and phishing. Returns `spam`, `suspicious`, or `safe`. |
| `source_classifier.py` | Identifies who sent the email. Returns `internal`, `customer_external`, `broadcast_newsletter`, `automated_system`, or `unknown`. |
| `intent_classifier.py` | Determines why the email was sent. Returns `meeting_related`, `complaint`, `support_request`, `follow_up`, `reply_needed`, or `informational`. |
| `priority_classifier.py` | Assigns urgency level. Returns `high`, `medium`, or `low`. |
| `llm_classifier.py` | LLM-based fallback for ambiguous emails. Calls the configured LLM provider to resolve `unknown` or borderline source/intent labels. |
| `__init__.py` | Package init. |

## Classification Labels

All valid label values are defined in `utils/constants.py`:

```
SAFETY_LABELS  = ["spam", "suspicious", "safe"]
SOURCE_LABELS  = ["customer_external", "internal", "broadcast_newsletter", "automated_system", "unknown"]
INTENT_LABELS  = ["reply_needed", "informational", "meeting_related", "complaint", "support_request", "follow_up"]
PRIORITY_LABELS = ["high", "medium", "low"]
```

## Rule-Based vs LLM Classification

The first four classifiers use keyword rules and regex patterns, making them fast and deterministic. The `LLMIntentSourceClassifier` is triggered only when:

- The source label is `broadcast_newsletter` or `unknown`
- The intent label is `informational` or `unknown`
- The safety label is `suspicious`

This keeps LLM calls targeted and minimizes cost.

## How to Add a New Classifier

1. Create a new file, e.g., `sentiment_classifier.py`.
2. Implement a class with a `classify(email: CleanedEmail) -> str` method.
3. Add the new label list to `utils/constants.py`.
4. Import and call it in `pipeline/orchestrator.py`.
5. Add the new field to the `ClassificationResult` model in `models/email_models.py`.
