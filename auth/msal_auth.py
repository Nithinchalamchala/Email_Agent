"""
MSAL Device Code Flow authentication for Microsoft Graph.

First run:  prints a URL + code → you sign in once in the browser
All later runs:  silent refresh using the cached refresh token (no browser)

Refresh tokens issued by Entra ID are valid for 90 days of continuous use.
MSAL automatically renews the access token (60–90 min lifetime) using the
refresh token, so you never see an expiry error again after the first sign-in.

Required .env variables
-----------------------
  AZURE_CLIENT_ID   — Application (client) ID from your Azure app registration
  AZURE_TENANT_ID   — Directory (tenant) ID  (or "common" for personal accounts)

Azure app registration checklist
---------------------------------
  1. portal.azure.com → Azure Active Directory → App registrations → New
  2. Supported account types: "Accounts in this organizational directory only"
     (or "Multitenant" if needed)
  3. Platform: Mobile and desktop applications
     Redirect URI: https://login.microsoftonline.com/common/oauth2/nativeclient
  4. API Permissions (Delegated):
       Mail.Read, Mail.ReadWrite, User.Read
     Grant admin consent if required by your tenant.
  5. Copy "Application (client) ID" → AZURE_CLIENT_ID
     Copy "Directory (tenant) ID"   → AZURE_TENANT_ID
"""

import os
import json
import msal
from dotenv import load_dotenv

load_dotenv()

SCOPES     = ["Mail.Read", "Mail.ReadWrite", "User.Read"]
CACHE_PATH = os.path.join(os.path.dirname(__file__), ".token_cache.json")


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            cache.deserialize(f.read())
    return cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        with open(CACHE_PATH, "w") as f:
            f.write(cache.serialize())


def _build_app(cache: msal.SerializableTokenCache) -> msal.PublicClientApplication:
    client_id = os.environ.get("AZURE_CLIENT_ID", "").strip()
    tenant_id = os.environ.get("AZURE_TENANT_ID", "common").strip()

    if not client_id:
        raise EnvironmentError(
            "\n"
            "  [MSAL] AZURE_CLIENT_ID is not set.\n"
            "  Add these two lines to your .env file:\n"
            "    AZURE_CLIENT_ID=<your-app-client-id>\n"
            "    AZURE_TENANT_ID=<your-tenant-id>\n"
            "  See auth/msal_auth.py for the Azure portal setup steps.\n"
        )

    return msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def acquire_token() -> str:
    """
    Return a valid Microsoft Graph access token.

    - Checks the on-disk token cache first.
    - If the access token is expired, refreshes it silently via the cached
      refresh token (no user interaction needed).
    - If no cache exists (first run or cache deleted), initiates Device Code
      Flow — prints a short URL + code and waits for the user to sign in.
    """
    cache   = _load_cache()
    app     = _build_app(cache)
    result  = None

    # 1. Try silent acquisition (uses cached refresh token)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    # 2. Silent failed or no cache → Device Code Flow (one-time browser sign-in)
    if not result or "access_token" not in result:
        flow = app.initiate_device_flow(scopes=SCOPES)

        if "user_code" not in flow:
            raise RuntimeError(
                f"Failed to initiate Device Code Flow: "
                f"{flow.get('error_description', flow)}"
            )

        print()
        print("=" * 60)
        print("  ONE-TIME MICROSOFT SIGN-IN REQUIRED")
        print("=" * 60)
        print()
        print(f"  1. Open this URL in your browser:")
        print(f"     {flow.get('verification_uri', 'https://microsoft.com/devicelogin')}")
        print()
        print(f"  2. Enter this code when prompted:")
        print(f"     {flow.get('user_code', '(see above)')}")
        print()
        print("  This script will continue automatically after sign-in.")
        print("  All future runs will be fully silent.")
        print("=" * 60)
        print()

        # Blocks here until the user completes the browser sign-in
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        error = result.get("error_description") or result.get("error") or str(result)
        raise RuntimeError(f"Authentication failed: {error}")

    _save_cache(cache)
    return result["access_token"]


def get_authenticated_user() -> dict:
    """
    Return info about the signed-in user from the token cache.
    Returns an empty dict if no cached session exists.
    Does NOT trigger a new sign-in.
    """
    cache = _load_cache()
    try:
        app      = _build_app(cache)
        accounts = app.get_accounts()
        if accounts:
            acct = accounts[0]
            return {
                "email": acct.get("username", ""),
                "name":  acct.get("name", ""),
            }
    except Exception:
        pass
    return {}


def revoke_session() -> None:
    """
    Delete the token cache, effectively signing out.
    Next call to acquire_token() will trigger the Device Code Flow again.
    """
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
        print("Token cache deleted. You will be prompted to sign in on the next run.")
    else:
        print("No active session found.")
