# TraceLab Frontend

React + TypeScript frontend for the TraceLab dataset reproducibility platform.

The interface allows users to:

- browse datasets and immutable dataset versions
- upload new CSV versions
- view asynchronous processing status
- inspect schema and data-quality metrics
- visualize null values with Plotly
- inspect provenance and processing metadata

## Stack

- React
- TypeScript
- Vite
- Plotly.js
- ESLint
- nginx for the production container

## Development

Install dependencies and start the development server:

```bash
npm ci
npm run dev
```

The development application runs at:

```text
http://localhost:5173
```

The backend API is configured through `VITE_API_BASE_URL`.

## Quality Checks

```bash
npm run lint
npm run build
```

For the complete application, including the API, PostgreSQL, Redis and background worker, run Docker Compose from the repository root.