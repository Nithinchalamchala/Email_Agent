# outlook

Reserved for additional Microsoft Outlook / Office 365 integration utilities.

## Planned Purpose

This module will contain all Office 365 and Microsoft Graph API integration code. The initial fetch logic currently lives in `fetch_unread_o365.py` at the project root and will be migrated here as it grows. Planned components include:

- **Authentication helpers**: Utilities for obtaining and refreshing Microsoft Graph API tokens using OAuth 2.0 (client credentials or device code flow).
- **Email fetcher**: A clean class-based wrapper around the Graph API `/me/messages` endpoint with configurable filters (unread, date range, folder).
- **Email sender**: Sending approved draft replies back through the Graph API to the original sender.
- **Read status sync**: Marking emails as read after they have been processed by the pipeline.
- **Folder management**: Moving processed emails to designated O365 folders for archiving.

## Current State

This directory is empty. The `fetch_unread_o365.py` script at the project root currently handles email fetching using a bearer token from the `MS_GRAPH_TOKEN` environment variable. That logic will be refactored into a structured module here.
