# TraceLab — System Architecture

## 1. Architecture Goals

TraceLab is designed as a production-style full-stack application for
reproducible dataset processing, data-quality monitoring, dataset versioning,
and data lineage.

The architecture prioritizes:

- reproducibility,
- maintainability,
- asynchronous processing,
- traceability,
- testability,
- failure isolation,
- and a clear path from local development to cloud deployment.

The initial implementation uses a modular monolith with a separate
background worker.

This keeps operational complexity low while maintaining clear boundaries
between application responsibilities.


## 2. High-Level Architecture

                    ┌─────────────────────┐
                    │       Browser       │
                    └──────────┬──────────┘
                               │
                               │ HTTP / REST
                               ▼
                    ┌─────────────────────┐
                    │ React + TypeScript  │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                               │ REST / JSON
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │        API          │
                    └─────┬────────┬──────┘
                          │        │
                          │        │ enqueue job
                          │        ▼
                          │   ┌──────────────┐
                          │   │    Redis     │
                          │   │    Queue     │
                          │   └──────┬───────┘
                          │          │
                          │          ▼
                          │   ┌──────────────┐
                          │   │  RQ Worker   │
                          │   └──────┬───────┘
                          │          │
                          ▼          ▼
                    ┌─────────────────────┐
                    │     PostgreSQL      │
                    └─────────────────────┘

                              Worker
                                │
                                ▼
                       ┌─────────────────┐
                       │  File Storage   │
                       └─────────────────┘


## 3. Architectural Style

TraceLab will initially use a modular monolith.

The backend is deployed as one application codebase, while background
processing runs in a separate worker process using the same domain and
application code.

The application is divided internally into clear modules and layers.

This approach was selected instead of microservices because the initial
application does not require independently deployable services.

A modular monolith provides:

- simpler local development,
- simpler deployment,
- easier transactions,
- lower operational overhead,
- and clear internal boundaries.

If future scale or organizational requirements justify independent services,
modules can later be extracted behind well-defined interfaces.


## 4. Frontend

### Technology

- React
- TypeScript
- Plotly.js
- Vite

### Responsibilities

The frontend is responsible for:

- project and dataset navigation,
- dataset upload,
- processing-status visualization,
- data-quality dashboards,
- dataset version comparison,
- interactive visualizations,
- and lineage visualization.

The frontend communicates with the backend exclusively through the HTTP API.

It must not access PostgreSQL, Redis, or file storage directly.


## 5. API Layer

### Technology

FastAPI

### Responsibilities

The API is responsible for:

- accepting and validating HTTP requests,
- exposing REST endpoints,
- serializing responses,
- mapping application errors to HTTP responses,
- initiating application use cases,
- and enqueueing long-running processing operations.

The API should remain thin.

Business rules should not be implemented directly inside route handlers.


## 6. Backend Layers

The backend will use the following logical flow:

    HTTP Request
         │
         ▼
       Router
         │
         ▼
       Service
         │
         ▼
     Repository
         │
         ▼
     PostgreSQL


### Router Layer

Responsible for HTTP-specific concerns.

Examples:

- request parsing,
- response models,
- status codes,
- dependency injection,
- and HTTP error mapping.


### Service Layer

Responsible for application and business logic.

Examples:

- creating datasets,
- assigning dataset versions,
- detecting duplicate uploads,
- starting processing workflows,
- comparing dataset versions,
- and enforcing application rules.


### Repository Layer

Responsible for persistence.

Examples:

- database queries,
- inserting entities,
- retrieving entities,
- and persistence-specific operations.

Business rules should not depend directly on SQL queries.


## 7. PostgreSQL

PostgreSQL is the system's primary persistent metadata store.

It stores entities such as:

- projects,
- datasets,
- dataset versions,
- processing jobs,
- quality results,
- and lineage events.

Large uploaded dataset files will not be stored directly inside PostgreSQL.

PostgreSQL stores metadata describing those files and their processing state.


## 8. File Storage

Dataset files are stored separately from application metadata.

For local development, files may initially be stored on a mounted filesystem.

The application should access files through a storage abstraction rather
than directly depending on local filesystem paths.

Conceptually:

    Storage
       │
       ├── LocalStorage
       │
       └── ObjectStorage (future)

This allows local storage to later be replaced by services such as
Amazon S3 without changing the application's core business logic.


## 9. Asynchronous Processing

Dataset processing may involve:

- reading large CSV files,
- calculating checksums,
- schema inference,
- data-quality calculations,
- and generating metadata.

These operations should not block an HTTP request.

Therefore processing follows:

    API
     │
     │ enqueue
     ▼
    Redis
     │
     ▼
   RQ Worker
     │
     ▼
   Processing


The API should return quickly after accepting an upload.

Example response:

    HTTP 202 Accepted

    {
      "job_id": "...",
      "status": "queued"
    }

The client can retrieve processing status separately.


## 10. Processing Job State Machine

Processing jobs have explicit states:

                  ┌──────────┐
                  │  QUEUED  │
                  └────┬─────┘
                       │
                       ▼
                ┌────────────┐
                │ PROCESSING │
                └──────┬─────┘
                       │
                 ┌─────┴─────┐
                 │           │
                 ▼           ▼
          ┌───────────┐ ┌─────────┐
          │ COMPLETED │ │ FAILED  │
          └───────────┘ └─────────┘


A failed job must retain enough information to diagnose the failure.

Job failures must not corrupt previously completed dataset versions.


## 11. Dataset Versioning

Dataset versions are immutable.

A logical dataset may contain multiple versions:

    Dataset
       │
       ├── Version 1
       ├── Version 2
       └── Version 3


Uploading new data creates a new version rather than modifying an existing
version.

Each version records metadata including:

- version number,
- original filename,
- file checksum,
- file location,
- row count,
- column count,
- inferred schema,
- creation timestamp,
- pipeline version,
- and processing status.


## 12. File Identity and Idempotency

TraceLab calculates a SHA-256 checksum for uploaded file content.

Example:

    SHA256(file bytes)
            │
            ▼
    e3b0c44298fc...


The checksum provides a content-based identity independent of the filename.

This can be used to detect repeated uploads of identical content.

The application should not rely on filenames to determine whether two
datasets are identical.


## 13. Data Quality Processing

Initial data-quality processing includes:

- file readability,
- row count,
- column count,
- inferred data types,
- missing-value counts,
- missing-value percentages,
- duplicate-row counts,
- and validation warnings.

Quality results belong to a specific dataset version.

This means quality metrics can be compared between versions.


## 14. Data Lineage

TraceLab records how dataset versions and outputs were produced.

A simplified lineage graph may look like:

    Source File
         │
         ▼
      Upload
         │
         ▼
     Validation
         │
         ▼
   Transformation
         │
         ▼
   Dataset Version
         │
         ▼
    Visualization


Lineage metadata may include:

- input dataset version,
- output dataset version,
- processing operation,
- timestamp,
- pipeline version,
- code version,
- and processing job.


## 15. Reproducibility

TraceLab should make it possible to determine which data and software
produced a result.

Relevant metadata includes:

- dataset version,
- SHA-256 checksum,
- pipeline version,
- application version or Git commit,
- processing timestamp,
- and transformation configuration.

A future reproduction manifest may expose this information in a
machine-readable format.


## 16. Error Handling

Errors should be handled at the appropriate layer.

Examples:

### HTTP errors

    400 Bad Request
    404 Not Found
    409 Conflict
    422 Validation Error

### Processing failures

Worker failures should update the processing job to:

    FAILED

and store diagnostic information.

Internal exceptions should be logged but should not expose sensitive
implementation details to API clients.


## 17. Observability

The application should produce structured logs.

Important events include:

- dataset upload accepted,
- dataset version created,
- job queued,
- processing started,
- validation completed,
- processing completed,
- and processing failed.

Each processing operation should include identifiers such as:

- project_id,
- dataset_id,
- dataset_version_id,
- and job_id.

This makes operations traceable across application components.


## 18. Testing Strategy

TraceLab will use multiple testing levels.

### Unit Tests

Test isolated business logic.

Examples:

- checksum calculation,
- quality calculations,
- version comparison,
- and validation rules.


### Integration Tests

Test components working together.

Examples:

- repository + PostgreSQL,
- service + repository,
- worker + database.


### API Tests

Test the application from its HTTP interface.

Example:

    POST /datasets
        ↓
    HTTP 201
        ↓
    dataset persisted


### End-to-End Tests

A small number of tests may eventually validate critical user journeys:

    upload
      ↓
    process
      ↓
    inspect quality results


## 19. Local Deployment

The local environment will eventually contain:

    docker compose

        ├── frontend
        ├── api
        ├── worker
        ├── postgres
        └── redis


A developer should be able to start the complete system with minimal
manual configuration.


## 20. Production Evolution

The local architecture should have a straightforward path to cloud
infrastructure.

Conceptually:

    React
      │
      ▼
    CDN / Static Hosting

    FastAPI
      │
      ▼
    Container Service

    Worker
      │
      ▼
    Container Worker

    PostgreSQL
      │
      ▼
    Managed PostgreSQL

    Redis
      │
      ▼
    Managed Redis

    File Storage
      │
      ▼
    Object Storage


The exact cloud provider is intentionally not part of the core architecture.