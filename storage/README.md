# storage

Reserved for future persistent storage and result archiving.

## Planned Purpose

This module will provide a unified interface for storing and retrieving pipeline inputs and outputs. Planned capabilities include:

- **Result persistence**: Writing `PipelineOutput` records to a database (PostgreSQL, SQLite) or object storage (S3, GCS) rather than the current file-based output in `sample_data/batch/`.
- **Email deduplication**: Tracking processed message IDs to avoid reprocessing emails seen in previous runs.
- **Draft history**: Storing generated drafts alongside original emails for audit and review workflows.
- **Query interface**: Retrieving processed emails by filter criteria (date range, sender, action type, priority) to support the dashboard and reporting.

## Current State

This directory is empty. The current pipeline writes results as individual JSON files in `sample_data/batch/results/` and `sample_data/batch/outputdraft/`. Storage abstraction will be introduced here when a persistent backend is needed.
