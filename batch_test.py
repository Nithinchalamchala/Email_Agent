import os
import json
from datetime import datetime, timezone
from pipeline.orchestrator import email_pipeline
from storage.database import init_db, insert_email

BATCH_DIR = "sample_data/batch"

def run_batch():
    init_db()
    files = [
        f for f in os.listdir(BATCH_DIR)
        if f.endswith(".json")
        and not f.startswith("result")
        and os.path.isfile(os.path.join(BATCH_DIR, f))
    ]
    for f in sorted(files):
        print("=" * 60)
        print(f"INPUT FILE: {f}")
        with open(os.path.join(BATCH_DIR, f)) as fin:
            data = json.load(fin)

        email_id = f.replace(".json", "")
        result = email_pipeline(data)
        print(json.dumps(result, indent=2))

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
            "sender":                data.get("sender", ""),
            "subject":               data.get("subject", ""),
            "body":                  data.get("body", ""),
            "received_date":         data.get("timestamp"),
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
            "original_email":        json.dumps(data),
            "processed_at":          datetime.now(timezone.utc).isoformat(),
            "source_type":           "batch_test",
        })
        print(f"Saved to DB: {email_id}")
        print("=" * 60)

if __name__ == "__main__":
    run_batch()
