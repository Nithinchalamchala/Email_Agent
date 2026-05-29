#!/usr/bin/env python3
"""
Main entry for the Hermes Email Intelligence Pipeline.
Usage: python main.py sample_data/sample_email.json
"""
import json
import sys
import os
from datetime import datetime, timezone
from pipeline.orchestrator import email_pipeline
from storage.database import init_db, insert_email
from utils.logger import logger

def main(email_json_path: str):
    init_db()
    with open(email_json_path) as f:
        email_data = json.load(f)

    result = email_pipeline(email_data)
    print(json.dumps(result, indent=2))

    email_id = os.path.splitext(os.path.basename(email_json_path))[0]
    clf = result.get("classification", {}) or {}
    pipeline_output = {
        k: result[k]
        for k in ("classification", "action", "draft", "summary",
                  "reasoning", "requires_human_review")
        if k in result
    }
    if result.get("llm_classification"):
        pipeline_output["llm_classification"] = result["llm_classification"]

    insert_email({
        "id":                    email_id,
        "sender":                email_data.get("sender", ""),
        "subject":               email_data.get("subject", ""),
        "body":                  email_data.get("body", ""),
        "received_date":         email_data.get("timestamp"),
        "is_read":               0,
        "safety":                clf.get("safety", ""),
        "source":                clf.get("source", ""),
        "intent":                clf.get("intent", ""),
        "priority":              clf.get("priority", ""),
        "action":                result.get("action", ""),
        "requires_human_review": 1 if result.get("requires_human_review") else 0,
        "draft":                 result.get("draft"),
        "summary":               result.get("summary"),
        "reasoning":             result.get("reasoning"),
        "pipeline_output":       json.dumps(pipeline_output),
        "original_email":        json.dumps(email_data),
        "processed_at":          datetime.now(timezone.utc).isoformat(),
        "source_type":           "manual",
    })
    logger.info(f"Saved to DB: {email_id}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python main.py sample_data/sample_email.json")
        exit(1)
    main(sys.argv[1])
