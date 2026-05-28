# notifications

Reserved for future notification dispatch logic.

## Planned Purpose

This module will handle sending outbound notifications when the pipeline completes processing or when a generated draft requires human review. Planned channels include:

- **Telegram**: Send a message to a configured chat or user when a high-priority email is processed. A basic Telegram notification is already present inline in `fetch_unread_o365.py` and will be refactored here.
- **Slack**: Post a notification to a designated channel for emails flagged as `requires_human_review = True`.
- **Email**: Send a digest notification of emails processed during a batch run.
- **Webhook**: POST a JSON payload to any configured endpoint for integration with external systems.

## Planned Interface

All notification handlers will implement a common interface:

```python
class NotificationHandler:
    def notify(self, pipeline_output: PipelineOutput, original_email: RawEmail) -> None:
        ...
```

The pipeline orchestrator will call registered handlers after each email is processed.

## Current State

This directory is empty. The Telegram notification call in `fetch_unread_o365.py` is the only existing notification logic. It will be extracted into a proper handler class here in a future iteration.
