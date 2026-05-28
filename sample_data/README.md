# sample_data

This directory contains test fixtures and pipeline outputs used during development, testing, and dashboard visualization.

## Structure

```
sample_data/
├── sample_email.json          A single sample email in RawEmail format. Used with main.py.
├── expected_output.json       The expected pipeline output for sample_email.json.
└── batch/
    ├── test1_spam.json         Batch test: spam email
    ├── test2_newsletter.json   Batch test: newsletter
    ├── test3_support.json      Batch test: support request
    ├── test4_meeting_internal.json
    ├── test5_complaint.json
    ├── test6_auto_ack.json
    ├── test7_system_maintenance.json
    ├── test8_followup.json
    ├── test9_misc.json
    ├── test10_fyi.json
    ├── test11_phishing.json
    ├── test12_job_application.json
    ├── test13_partnership.json
    ├── test14_security_alert.json
    ├── test15_outage_apology.json
    ├── test16_tech_explain.json
    ├── test17_price_negotiation.json
    ├── test18_vip_onboarding.json
    ├── raw_o365_emails.json    Raw dump from fetch_unread_o365.py (Office 365 API response)
    ├── results/                Pipeline outputs from batch_test.py (one _result.json per email)
    └── outputdraft/            Pipeline outputs from fetch_unread_o365.py (live O365 emails)
```

## File Format

Each test fixture in `batch/` is a JSON object matching the `RawEmail` schema:

```json
{
  "sender": "user@example.com",
  "subject": "Subject line",
  "body": "Email body text...",
  "timestamp": "2024-01-01T10:00:00Z",
  "thread_id": "thread-001",
  "metadata": {}
}
```

## Result File Format

Files in `results/` and `outputdraft/` are named `{email_id}_result.json` and contain the full `PipelineOutput` dict plus the original email fields (`original_sender`, `original_subject`, `original_body`, `original_timestamp`).

## Running the Batch Tests

```bash
python batch_test.py
```

This processes all files in `batch/` (excluding subdirectories) through the full pipeline and writes results to `batch/results/`.
