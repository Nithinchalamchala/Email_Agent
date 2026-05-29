"""
CLI script: fetch unread O365 emails and run through the Hermes pipeline.

Authentication: MSAL Device Code Flow (auth/msal_auth.py)
  - First run : one-time browser sign-in
  - All later runs: silent token refresh

For browser-based auth (recommended), use the dashboard instead:
  open http://localhost:3000 → Sign in with Microsoft → Fetch Emails
"""
from dotenv import load_dotenv
load_dotenv()

from auth.msal_auth import acquire_token
from services.graph_fetcher import fetch_and_process
from storage.database import init_db


def main() -> None:
    init_db()

    print("Authenticating with Microsoft Graph…")
    token = acquire_token()
    print("Authenticated.\n")

    results = fetch_and_process(token=token, limit=10)

    new_count = len(results["processed"])
    skipped   = len(results["skipped"])

    print(f"Done — {new_count} new email(s) processed, {skipped} already in DB.\n")
    for e in results["processed"]:
        print(f"  [{e['action'][:20]:<20}]  {e['subject'][:55]}")


if __name__ == "__main__":
    main()
