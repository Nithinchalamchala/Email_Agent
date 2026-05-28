# decision_engine

This module maps a `ClassificationResult` to a concrete workflow action. It answers the question: given what we know about this email, what should the pipeline actually do with it?

## Files

| File | Purpose |
|---|---|
| `workflow_router.py` | Contains the rule table (`RULES`) and the `route_workflow` function. |
| `__init__.py` | Package init. |

## How Routing Works

`route_workflow(classification)` iterates through the `RULES` list and returns the first matching rule. Each rule is a tuple of:

```
( (safety, source, intent, priority), action, requires_human_review, reasoning )
```

A `None` in any position is a wildcard that matches any value. This keeps the rule table readable and easy to modify.

## Current Rules

| Safety | Source | Intent | Priority | Action | Human Review |
|---|---|---|---|---|---|
| `spam` | any | any | any | `ignore` | No |
| any | `broadcast_newsletter` | any | any | `summarize_only` | No |
| any | any | any | any | `generate_draft_and_notify` | Yes |

The last rule is a catch-all. Every email that is not spam and not a newsletter gets a draft generated and flagged for human review.

## Workflow Actions

| Action | Description |
|---|---|
| `ignore` | Discard. No LLM call, no draft, no output. |
| `summarize_only` | Call the LLM for a summary. No reply draft. |
| `generate_draft` | Generate a reply draft. |
| `generate_draft_and_notify` | Generate a reply draft and flag for human review. |
| `notify_only` | Send a notification with no draft. |

## How to Add Rules

Insert a new tuple into the `RULES` list in `workflow_router.py` before the catch-all entry. For example, to handle internal high-priority emails separately:

```python
((None, "internal", None, "high"), "generate_draft_and_notify", True, "High-priority internal email."),
```

Rules are evaluated top-to-bottom, so more specific rules should come first.
