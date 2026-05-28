from dotenv import load_dotenv
load_dotenv()
import os
from O365 import Account

scopes = [
    'https://graph.microsoft.com/Mail.Read'
]
    
credentials = (
    os.environ['O365_CLIENT_ID'],
    os.environ['O365_CLIENT_SECRET']
)
tenant_id = os.environ['O365_TENANT_ID']
    
account = Account(credentials, tenant_id=tenant_id)
    
if not account.is_authenticated:
    account.authenticate(scopes=scopes)
else:
    print("O365 authentication already set up and token cached.")
    
print("Connected to Microsoft Account!")
    