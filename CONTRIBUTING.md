# Contributing to TraceLab

Contributions, suggestions and bug reports are welcome.

## Development

Run the complete application with Docker Compose:

```bash
docker compose up --build
```

### Backend

The backend requires Python 3.12+.

```bash
cd backend
pip install -e ".[dev]"
ruff check app tests
pytest -v
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run build
```

## Database changes

TraceLab uses Alembic for database migrations. Existing migrations should not be modified after they have been committed. Create a new migration for schema changes:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Pull requests

Please keep changes focused and ensure backend tests, linting, and the frontend production build pass before submitting a pull request.

Changes to dataset processing should preserve TraceLab's core reproducibility principles: immutable dataset versions, SHA-256 content identity, processing-job tracking and provenance metadata.

## License

Contributions are licensed under the MIT License.