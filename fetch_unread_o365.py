from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from pipeline.orchestrator import email_pipeline

def send_telegram_alert(subject, context, record_id=None):
    from hermes_tools import send_message
    msg = f"\ud83d\udceb [INFO/REMINDER] New Informational Email Received\n\n" \
          f"Subject: {subject}\n" \
          f"Summary: {context}\n"
    if record_id:
        dashboard_url = f"https://YOUR_DASHBOARD_URL/email/{record_id}"
        msg += f"\n[Open in Dashboard]({dashboard_url})"
    send_message(action="send", message=msg, target="telegram:ANJANINITHIN CHALAMCHALA (dm)")

MS_GRAPH_TOKEN = os.environ['MS_GRAPH_TOKEN']
RAW_O365_OUTPUT_PATH = 'sample_data/batch/raw_o365_emails.json'

def get_email_body(msg_id, token):
    url = f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}?$select=body,subject"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    resp_json = resp.json()
    return resp_json, resp_json.get("body", {})

def html_to_text(html_content):
    if not html_content:
        return ''
    return BeautifulSoup(html_content, "html.parser").get_text(separator="\n", strip=True)

def fetch_unread_emails(limit=10):
    url = (
        "https://graph.microsoft.com/v1.0/me/messages?"
        "$filter=isRead eq false&$top=" + str(limit) + "&$select=id,sender,subject,receivedDateTime,conversationId,internetMessageId"
    )
    headers = {
        "Authorization": f"Bearer {MS_GRAPH_TOKEN}",
        "Accept": "application/json"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    items = resp.json().get('value', [])
    raw_dump = []
    emails = []
    for item in items:
        full_msg_json, body_obj = get_email_body(item["id"], MS_GRAPH_TOKEN)
        html_body = body_obj.get('content', '')
        plain_body = html_to_text(html_body) if html_body else ''
        subject = item.get('subject', '') or item.get('Subject', '')
        if not subject:
            subject = full_msg_json.get('subject', '')
        sender = (item.get('sender', {}) or {}).get('emailAddress', {}).get('address', '')
        timestamp = item.get('receivedDateTime', datetime.utcnow().isoformat())
        thread_id = item.get('conversationId', '')
        if not plain_body and html_body:
            plain_body = '[HTML only, see original_html_body]'
        emails.append({
            'sender': sender,
            'subject': subject,
            'body': plain_body,
            'timestamp': timestamp,
            'thread_id': thread_id,
            'metadata': {
                'id': item.get('id', ''),
                'internetMessageId': item.get('internetMessageId', '')
            },
            'raw_html_body': html_body,
            'full_msg': full_msg_json
        })
        raw_dump.append({'summary': item, 'full_msg': full_msg_json})
    with open(RAW_O365_OUTPUT_PATH, 'w') as f:
        json.dump(raw_dump, f, indent=2)
    return emails

def main():
    RESULTS_DIR = "sample_data/batch/outputdraft"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    emails = fetch_unread_emails(limit=10)
    print(f"Fetched {len(emails)} unread emails from O365.")
    for email in emails:
        result = email_pipeline(email)
        # Always propagate the truly correct originals, using robust keys
        result["original_subject"] = email.get("subject", "") or (email.get("full_msg", {}).get("subject", ""))
        result["original_body"] = email.get("body", "")
        result["original_sender"] = email.get("sender", "")
        result["original_timestamp"] = email.get("timestamp", "")
        result["original_thread_id"] = email.get("thread_id", "")
        result["original_html_body"] = email.get("raw_html_body", "")
        result["full_msg"] = email.get("full_msg", {})
        # --- TELEGRAM NOTIFY FOR "inform" INTENT ---
        if result.get("classification", {}).get("intent", "") == "inform":
            short_body = result.get("original_body") or html_to_text(result.get("original_html_body", ""))
            short_body = (short_body or "(No summary)")[:200]
            record_id = email['metadata'].get('id', '') or email['thread_id']
            send_telegram_alert(result["original_subject"], short_body, record_id)
        outname = email['metadata'].get('id', '') or email['thread_id']
        fname = f"{outname}_result.json"
        path = os.path.join(RESULTS_DIR, fname)
        with open(path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Saved output draft: {path}")

if __name__ == "__main__":
    main()
