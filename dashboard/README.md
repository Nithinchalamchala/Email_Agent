# dashboard

The dashboard provides a visual interface for reviewing batch-processed email results. It consists of a FastAPI backend that serves processed email data and a React frontend that displays it.

## Files

| File | Purpose |
|---|---|
| `app.py` | FastAPI application exposing two REST endpoints for the frontend. |
| `frontend/` | React + TypeScript frontend built with Ant Design. See [frontend/README.md](frontend/README.md). |

## Backend (app.py)

The FastAPI app reads from `sample_data/hermes.db` (SQLite). Run `python -m storage.migrate` once to seed it from existing JSON files.

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/batch` | GET | Paginated email list. Query params: `page`, `limit`, `filter` (today/yesterday/7days/unread/important/ai_replied/pending_review/all), `search`, `priority`, `safety`, `action`. |
| `/api/stats` | GET | Global counts: total, unread, needs_review, high_priority. |
| `/api/email/{email_id}` | GET | Full pipeline result for one email including original body + AI draft. |
| `/api/email/{email_id}/mark-read` | PATCH | Mark email as read in DB. |

## Starting the Dashboard

### Backend

```bash
# From the project root (--app-dir . is required so storage/ is importable)
uvicorn dashboard.app:app --app-dir . --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd dashboard/frontend
npm install
npm start
```

The frontend dev server will start at `http://localhost:3000` and proxy API calls to the backend on port 8000.

Alternatively, the pre-built static frontend (in `frontend/build/`) can be served directly by the FastAPI app or any static file server.
