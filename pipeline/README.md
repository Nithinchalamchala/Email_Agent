# pipeline

This module contains the central orchestrator that connects every stage of the Hermes pipeline into a single callable function.

## Files

| File | Purpose |
|---|---|
| `orchestrator.py` | Defines `email_pipeline(raw_email_dict)`, the main pipeline function called by `main.py`, `fetch_unread_o365.py`, and `batch_test.py`. |
| `__init__.py` | Package init. |

## Pipeline Execution Order

`email_pipeline` executes these steps sequentially:

1. Validate the raw email dict into a `RawEmail` Pydantic model.
2. Clean the email body via `preprocessing.parser.preprocess_email`, returning a `CleanedEmail`.
3. Run all four classifiers (`SafetyClassifier`, `SourceClassifier`, `IntentClassifier`, `PriorityClassifier`) against the `CleanedEmail`.
4. If any classifier returns an ambiguous or borderline label, pass the email to `LLMIntentSourceClassifier` to refine the source and intent labels.
5. Combine all labels into a `ClassificationResult`.
6. Route the classification through `decision_engine.workflow_router.route_workflow` to get a `WorkflowAction`.
7. Build an `LLMContext` via `context.context_builder.build_llm_context`.
8. If the action is `generate_draft` or `generate_draft_and_notify`, call the configured LLM provider to generate a draft and summary.
9. If the action is `summarize_only`, call the LLM provider for a summary only.
10. Package everything into a `PipelineOutput` and return it as a plain dict.

## Return Value

The pipeline returns a Python dict that serializes directly to JSON with the following top-level keys:

```json
{
  "classification": { "safety": "...", "source": "...", "intent": "...", "priority": "..." },
  "action": "generate_draft_and_notify",
  "draft": "...",
  "summary": "...",
  "reasoning": "...",
  "requires_human_review": true,
  "llm_classification": { ... }
}
```

The `llm_classification` key is only present when the LLM fallback classifier was invoked.

## LLM Provider Selection

The provider is selected at import time based on the `LLM_PROVIDER` environment variable. Setting `LLM_PROVIDER=gemini` loads `GeminiProvider`; any other value loads `OpenAIProvider`. Both implement the `LLMProvider` abstract base class.
