# prompts

Reserved for externalized prompt templates.

## Planned Purpose

This module will store prompt templates as separate files rather than keeping them hardcoded in `llm/prompt_builder.py`. Externalizing prompts makes it possible to:

- Edit prompt wording without touching Python code.
- Maintain different prompt variants for different email types (complaint vs. inquiry vs. meeting request).
- Version prompt templates independently of code deployments.
- A/B test prompt variations to improve draft quality.

## Planned Format

Templates will be stored as `.txt` or `.jinja2` files with named placeholders:

```
Email from: {{ sender }}
Subject: {{ subject }}
...
```

A template loader in this module will render the correct template based on the `ClassificationResult` (e.g., `complaint_draft.txt`, `support_draft.txt`, `newsletter_summary.txt`).

## Current State

This directory is empty. All prompts are currently built programmatically in `llm/prompt_builder.py`. Template externalization will be added here when prompt diversity grows beyond a single template.
