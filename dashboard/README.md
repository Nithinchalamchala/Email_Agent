# dashboard

The dashboard provides a visual interface for reviewing batch-processed email results. It consists of a FastAPI backend that serves processed email data and a React frontend that displays it.

## Files

| File | Purpose |
|---|---|
| `app.py` | FastAPI application exposing two REST endpoints for the frontend. |
| `frontend/` | React + TypeScript frontend built with Ant Design. See [frontend/README.md](frontend/README.md). |

## Backend (app.py)

The FastAPI app reads from two result directories:

- `sample_data/batch/results/` - Results from `batch_test.py`
- `sample_data/batch/outputdraft/` - Results from `fetch_unread_o365.py`

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/batch` | GET | Returns a summary list of all processed emails with metadata: sender, subject, action, priority, intent, safety, and whether human review is required. |
| `/api/email/{email_id}` | GET | Returns the full pipeline result for a single email by ID, including the original email body and the generated draft. |

Both endpoints match each result file to its original input file (same base filename without `_result.json`) to surface original sender and subject information.

## Starting the Dashboard

### Backend

```bash
# From the project root
uvicorn dashboard.app:app --reload --port 8000
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
