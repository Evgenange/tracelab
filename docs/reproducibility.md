# Reproducibility in TraceLab

TraceLab is designed to make dataset processing traceable and reproducible by preserving the identity of input data, recording immutable dataset versions, tracking asynchronous processing runs, and storing the resulting data-quality metadata.

The platform does not claim full FAIR compliance. Instead, it implements reproducibility and provenance mechanisms that are relevant to FAIR and open-science workflows.

## Reproducibility model

TraceLab represents dataset processing through the following relationship:

```text
Project
└── Dataset
    └── DatasetVersion
        ├── ProcessingJob
        └── QualityReport
```

A dataset represents a logical collection of data. Each uploaded file creates a new immutable `DatasetVersion`.

Processing is associated with that specific version rather than with the mutable dataset itself.

## Immutable dataset versions

Each uploaded dataset version records:

- dataset identifier
- version number
- original filename
- storage location
- SHA-256 checksum
- file size
- processing status
- creation timestamp

Once a version has been created, later uploads do not overwrite it. A new input becomes a new version.

This allows processing results and provenance metadata to remain associated with the exact input that produced them.

## Content identity with SHA-256

TraceLab calculates a SHA-256 checksum from the uploaded file contents.

The checksum provides a content-based identity for a dataset version rather than relying only on its filename.

For example:

```text
european_energy_generation.csv
        │
        ▼
SHA-256
        │
        ▼
25a77534124bda633db36dc49a08743...
```

TraceLab uses this checksum to detect an identical file that has already been registered for the same dataset.

This provides basic upload idempotency and prevents accidentally creating multiple versions containing identical file contents.

## Asynchronous processing

Dataset profiling is performed outside the HTTP request lifecycle.

The processing flow is:

```text
CSV upload
    │
    ▼
FastAPI
    │
    ├── store immutable dataset version
    ├── create ProcessingJob
    │
    ▼
Redis / RQ
    │
    ▼
Background worker
    │
    ▼
CSV profiling
    │
    ▼
QualityReport
```

This separation prevents potentially expensive data processing from blocking the API request.

A processing job records its state independently from the dataset version.

Typical job states are:

```text
queued → processing → completed
                    ↘ failed
```

The processing metadata includes identifiers and timestamps that allow a processing result to be associated with a particular execution.

## Data-quality profiling

The current CSV profiling pipeline calculates:

- row count
- column count
- duplicate-row count
- total null count
- null count per column
- inferred column schema
- numeric summary statistics

The resulting `QualityReport` is persisted in PostgreSQL and associated with the corresponding `DatasetVersion`.

This means quality results remain linked to the exact source file from which they were calculated.

## Provenance

TraceLab exposes provenance information for processed dataset versions.

The provenance view combines persisted metadata describing:

- dataset identifier
- dataset-version identifier
- version number
- original source filename
- SHA-256 checksum
- file size
- dataset-version status
- dataset-version creation time
- processing-job identifier
- processing status
- processing start and completion timestamps
- quality-report identifier
- quality-report creation timestamp
- processing pipeline name
- processing pipeline version

The current profiling pipeline identifies itself as:

```text
tracelab-csv-profiler
version 0.1.0
```

Together, this information answers several important reproducibility questions:

```text
Which file was processed?
        ↓
Which immutable dataset version represented it?
        ↓
What was its content checksum?
        ↓
Which processing run handled it?
        ↓
Which pipeline version was used?
        ↓
What quality report was produced?
```

## Database reproducibility

TraceLab manages relational database schema changes using Alembic migrations.

Database changes are maintained as an append-only migration history rather than by modifying migrations that have already been applied.

A clean PostgreSQL database can therefore be reconstructed by running:

```bash
alembic upgrade head
```

The Docker Compose environment performs this migration step before the API starts.

This allows a fresh environment to reconstruct the expected database schema from version-controlled migration history.

## Environment reproducibility

TraceLab packages its runtime components using Docker.

The Docker Compose environment contains separate services for:

- PostgreSQL
- Redis
- database migrations
- FastAPI
- RQ worker
- React/nginx frontend

A clean environment can be started with:

```bash
docker compose up --build
```

This reduces dependence on developer-specific local installations and provides a repeatable environment for running the application.

## Storage model

Dataset files and relational metadata are deliberately separated.

PostgreSQL stores structured application metadata, while uploaded dataset files are stored through the application's storage service.

In the current Docker Compose implementation, API and worker containers share persistent dataset storage through a Docker volume.

This is suitable for local development and demonstration while keeping the application architecture open to a future object-storage implementation.

For example, the storage abstraction could later be backed by S3-compatible object storage without changing the conceptual dataset-version model.

## Reproducibility boundaries

TraceLab currently provides application-level mechanisms for:

- immutable dataset versioning
- content hashing
- duplicate-content detection
- processing-job tracking
- data-quality result persistence
- processing provenance
- database migration history
- containerized execution

There are deliberate limitations.

The current version:

- supports CSV datasets only
- uses shared local/container storage rather than distributed object storage
- does not provide authentication or authorization
- does not capture the complete operating-system or hardware environment of every processing execution
- does not implement a formal scientific workflow specification
- does not provide a complete FAIR-compliance framework

These limitations are intentionally kept explicit rather than overstating the guarantees provided by the platform.

## Open-science relevance

Scientific and research datasets often pass through multiple transformations before producing an analysis or visualization.

Without explicit versioning and provenance, it can become difficult to determine which input produced a particular result.

TraceLab demonstrates an engineering approach in which data identity, processing state and resulting metadata are treated as first-class application concepts.

The architecture is therefore relevant to research software, scientific data platforms and open-science workflows where traceability and reproducibility are important requirements.