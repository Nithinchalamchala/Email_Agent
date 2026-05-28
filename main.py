#!/usr/bin/env python3
"""
Main entry for the Hermes Email Intelligence Pipeline
"""
import json
import sys
from pipeline.orchestrator import email_pipeline
from utils.logger import logger

def main(email_json_path):
    with open(email_json_path) as f:
        email_data = json.load(f)
    result = email_pipeline(email_data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python main.py sample_data/sample_email.json")
        exit(1)
    main(sys.argv[1])
