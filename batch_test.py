import os
import json
from pipeline.orchestrator import email_pipeline

BATCH_DIR = "sample_data/batch"
RESULTS_DIR = "sample_data/batch/results"

os.makedirs(RESULTS_DIR, exist_ok=True)

def run_batch():
    files = [
        f for f in os.listdir(BATCH_DIR)
        if f.endswith(".json") and not f.startswith("result") and os.path.isfile(os.path.join(BATCH_DIR, f))
    ]
    for f in sorted(files):
        print("="*60)
        print(f"INPUT FILE: {f}")
        with open(os.path.join(BATCH_DIR, f), "r") as fin:
            data = json.load(fin)
        result = email_pipeline(data)
        # Propagate original fields robustly for dashboard/traceability
        result["original_subject"] = data.get("subject", "")
        result["original_body"] = data.get("body", "")
        result["original_sender"] = data.get("sender", "")
        result["original_timestamp"] = data.get("timestamp", "")
        result["original_thread_id"] = data.get("thread_id", "")
        # Optionally propagate O365/Graph-style nested body/content fields if present
        if "full_msg" in data and isinstance(data["full_msg"], dict):
            msg = data["full_msg"]
            if isinstance(msg.get("body"), dict) and msg["body"].get("content"):
                result["original_html_body"] = msg["body"]["content"]
        print(json.dumps(result, indent=2))
        result_path = os.path.join(RESULTS_DIR, f.replace(".json", "_result.json"))
        with open(result_path, "w") as fout:
            json.dump(result, fout, indent=2)
        print(f"Saved result: {result_path}")
        print("="*60)

if __name__ == "__main__":
    run_batch()
