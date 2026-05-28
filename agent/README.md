# agent

Reserved for future agentic loop and autonomous decision logic.

## Planned Purpose

This module will house higher-level agent orchestration that goes beyond the current single-pass pipeline. Planned capabilities include:

- **Autonomous email monitoring loop**: A long-running process that polls for new emails at a configured interval and runs each through the pipeline.
- **Multi-step decision chains**: Logic for emails that require multiple processing steps before a response can be drafted, such as fetching additional context or waiting for a prior thread to resolve.
- **Human-in-the-loop approval flow**: An agent that sends draft replies to a review queue and waits for approval before dispatching.
- **Feedback learning**: Tracking accepted vs. rejected drafts to improve classification and prompting over time.

## Current State

This directory is empty. The single-pass pipeline in `pipeline/orchestrator.py` currently handles all orchestration. Agent logic will be added here as the system evolves beyond one-shot processing.
