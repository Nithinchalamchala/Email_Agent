# dashboard/frontend

React + TypeScript frontend for the Hermes dashboard. Built with Create React App, Ant Design, and React Router.

## Technology Stack

| Library | Version | Purpose |
|---|---|---|
| React | 18 | UI framework |
| TypeScript | 5 | Type safety |
| Ant Design | 5 | UI component library |
| React Router | 6 | Client-side routing |

## Directory Structure

```
frontend/
├── public/
│   └── index.html          HTML shell
├── src/
│   ├── App.tsx             Root component with layout, routing, and header
│   ├── index.tsx           React entry point
│   ├── api.ts              API client functions for the FastAPI backend
│   └── components/
│       ├── EmailTable.tsx  Main view: sortable table of all batch results
│       └── EmailDetails.tsx Detail view: full email + generated draft for one email
├── build/                  Production build output (committed for easy static serving)
├── package.json
└── tsconfig.json
```

## Views

### Email Table (`/`)

Displays all processed emails in a table with columns for sender, subject, action, priority, intent, safety label, and human review flag. Clicking a row navigates to the detail view.

### Email Details (`/email/:id`)

Shows the full original email (sender, subject, body, timestamp) alongside the pipeline output: classification labels, workflow action, reasoning, and the generated draft reply.

## Development

```bash
npm install
npm start      # Dev server at http://localhost:3000
npm run build  # Production build into build/
```

The dev server proxies `/api/*` requests to `http://localhost:8000` where the FastAPI backend must be running.

## API Client

`src/api.ts` contains the typed fetch wrappers for the two backend endpoints. Update the base URL in that file if running the backend on a different host or port.
