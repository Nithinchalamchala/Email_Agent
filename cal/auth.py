import os
import json
import msal
from dotenv import load_dotenv

load_dotenv()

_CLIENT_ID = os.getenv("CLIENT_ID")
_TENANT_ID = os.getenv("TENANT_ID")
_AUTHORITY = f"https://login.microsoftonline.com/{_TENANT_ID}"
_SCOPES = ["Calendars.ReadWrite", "User.Read"]
_CACHE_FILE = os.path.join(os.path.dirname(__file__), "token_cache.json")


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if os.path.exists(_CACHE_FILE):
        with open(_CACHE_FILE) as f:
            cache.deserialize(f.read())
    return cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        with open(_CACHE_FILE, "w") as f:
            f.write(cache.serialize())


def _build_app(cache: msal.SerializableTokenCache) -> msal.PublicClientApplication:
    if not all([_CLIENT_ID, _TENANT_ID]):
        raise EnvironmentError("CLIENT_ID and TENANT_ID must be set in .env")
    return msal.PublicClientApplication(
        client_id=_CLIENT_ID,
        authority=_AUTHORITY,
        token_cache=cache,
    )


def get_access_token() -> str:
    """
    Acquires a delegated bearer token via the device code flow.

    On first call (no cache): prints a device-code sign-in URL and code to stdout,
    then blocks until the user completes sign-in in a browser.
    On subsequent calls: serves the token silently from token_cache.json until it
    expires, then repeats the device flow.

    Returns the raw access token string. Raises RuntimeError on failure.
    """
    cache = _load_cache()
    app = _build_app(cache)

    accounts = app.get_accounts()
    result = app.acquire_token_silent(scopes=_SCOPES, account=accounts[0] if accounts else None)

    if not result:
        flow = app.initiate_device_flow(scopes=_SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Device flow initiation failed: {flow.get('error_description', flow)}")
        print(flow["message"])  # prints: "To sign in, use a web browser to open … and enter code …"
        result = app.acquire_token_by_device_flow(flow)

    _save_cache(cache)

    if "access_token" not in result:
        error = result.get("error", "unknown_error")
        description = result.get("error_description", "No description provided.")
        raise RuntimeError(f"MSAL token acquisition failed [{error}]: {description}")

    return result["access_token"]


if __name__ == "__main__":
    token = get_access_token()
    print("Token acquired:", token[:20], "...")
