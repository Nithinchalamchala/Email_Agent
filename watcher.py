"""
Inbox watcher — polls fetch_unread_o365.py every POLL_INTERVAL seconds.
Runs the full email pipeline (+ calendar pipeline when intent=calendar)
on every new unread email automatically.

Usage:
    python watcher.py          # default 90s interval
    python watcher.py 60       # custom interval in seconds
"""
import sys
import time
import traceback
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

POLL_INTERVAL = int(sys.argv[1]) if len(sys.argv) > 1 else 90


def poll():
    from fetch_unread_o365 import main as fetch_main
    fetch_main()


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


if __name__ == "__main__":
    log(f"Watcher started — polling every {POLL_INTERVAL}s. Ctrl+C to stop.")
    log("Waiting for emails on vinayak.pareek@lumiq.ai ...")

    while True:
        try:
            log("Checking inbox ...")
            poll()
            log(f"Done. Next check in {POLL_INTERVAL}s.")
        except Exception as e:
            err = str(e)
            if "401" in err or "InvalidAuthenticationToken" in err or "Access token has expired" in err:
                log("ERROR: MS_GRAPH_TOKEN has expired. Refresh it in .env from Graph Explorer and restart.")
            else:
                log(f"ERROR during fetch: {e}")
                traceback.print_exc()
        time.sleep(POLL_INTERVAL)
