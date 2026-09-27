# TraceLab — System Requirements

## 1. Overview

TraceLab is an open-source platform for reproducible dataset processing,
data-quality monitoring, dataset versioning, and data lineage.

The system is intended for research and data teams that need to understand:

- what data was processed,
- where the data came from,
- which version was used,
- whether the data passed quality checks,
- and how a particular output can be reproduced.

The initial version of TraceLab will support CSV datasets.

---

## 2. Functional Requirements

Functional requirements describe what the system must do.

### FR-01 — Project Management

Users must be able to create a project.

A project groups related datasets and their processing history.

Example:

Project: European Sustainability Analysis

Datasets:
- Material Flow Accounts
- Emissions
- Population

---

### FR-02 — Dataset Registration

Users must be able to register a logical dataset within a project.

A dataset represents a collection of related dataset versions.

Example:

Dataset: Material Flow Accounts

Versions:
- v1
- v2
- v3

---

### FR-03 — Dataset Upload

Users must be able to upload a CSV file as a new version of a dataset.

The system must:

- accept CSV files,
- calculate a checksum for the uploaded file,
- create an immutable dataset version,
- store metadata about the uploaded file,
- and create a processing job.

---

### FR-04 — Dataset Versioning

Every successful dataset upload must create a new immutable dataset version.

Existing versions must never be overwritten.

Example:

Material Flow Accounts
├── v1
├── v2
└── v3

Each version must store metadata including:

- version number,
- original filename,
- file checksum,
- creation timestamp,
- processing status,
- row count,
- column count,
- and schema information.

---

### FR-05 — Asynchronous Processing

Dataset processing must run outside the HTTP request lifecycle.

After an upload, the API should return without waiting for the complete
dataset processing operation.

Processing jobs must have explicit states:

- queued,
- processing,
- completed,
- failed.

---

### FR-06 — Data Validation

The system must validate uploaded datasets.

Initial validation should include:

- CSV readability,
- column/schema detection,
- missing values,
- duplicate rows,
- row count,
- column count,
- and basic type inference.

Validation failures must not corrupt existing dataset versions.

---

### FR-07 — Data Quality Results

The system must store data-quality results for each dataset version.

Users must be able to inspect metrics such as:

- number of rows,
- number of columns,
- missing-value percentage,
- duplicate count,
- inferred column types,
- and validation warnings.

---

### FR-08 — Processing Job Status

Users must be able to retrieve the status of a processing job.

The API must expose whether a job is:

- queued,
- processing,
- completed,
- or failed.

If processing fails, the system should expose a useful error message.

---

### FR-09 — Dataset History

Users must be able to retrieve all versions belonging to a dataset.

Versions should be ordered chronologically.

---

### FR-10 — Version Comparison

Users must be able to compare two versions of the same dataset.

The comparison should initially include:

- row-count changes,
- column-count changes,
- schema changes,
- missing-value changes,
- and duplicate-count changes.

---

### FR-11 — Data Visualization

Users must be able to explore selected dataset variables through
interactive visualizations.

The frontend should support basic visualizations such as:

- distributions,
- time-series charts where appropriate,
- and comparisons between variables or dataset versions.

---

### FR-12 — Data Lineage

The system must record basic provenance information for dataset versions.

TraceLab should be able to identify:

- the source file,
- its checksum,
- when it was processed,
- which processing job produced the result,
- and which pipeline/software version processed it.

---

### FR-13 — Reproducibility Metadata

Each processed dataset version should contain enough metadata to identify
the data and software used to produce it.

This should include:

- dataset version,
- file checksum,
- processing timestamp,
- pipeline version,
- and application/code version where available.

---

## 3. Non-Functional Requirements

Non-functional requirements describe how the system should behave.

### NFR-01 — Reproducibility

Dataset versions must be immutable.

A dataset version that has already been processed must not silently change.

Given the same dataset version and processing version, it should be possible
to determine how an output was produced.

---

### NFR-02 — Traceability

Important processing operations must be traceable.

The system should retain metadata that allows a user to determine the origin
and processing history of a dataset version.

---

### NFR-03 — Reliability

A failed processing job must not corrupt existing data.

Failures should result in an explicit failed job state rather than leaving
the system in an unknown state.

---

### NFR-04 — Idempotency

The system should detect repeated uploads of identical file content using
a cryptographic checksum such as SHA-256.

Repeated requests must not accidentally create inconsistent system state.

---

### NFR-05 — Maintainability

The codebase should use clear separation of concerns.

Backend responsibilities should be separated between:

- API/HTTP handling,
- business logic,
- persistence,
- background processing,
- and data validation.

---

### NFR-06 — Testability

Core business logic must be testable independently from the user interface.

Automated tests should cover:

- business logic,
- API behavior,
- database operations,
- dataset validation,
- and critical integration paths.

---

### NFR-07 — Observability

The application must produce structured logs for important operations and
failures.

Processing jobs should expose sufficient information for diagnosing failures.

---

### NFR-08 — Security

Uploaded files must be treated as untrusted input.

The system must:

- validate supported file types,
- avoid trusting user-provided filenames,
- reject invalid input,
- and avoid exposing internal filesystem paths or implementation details.

Authentication and authorization are outside the initial MVP scope.

---

### NFR-09 — Portability

The complete development environment should be reproducible using containers.

A developer should eventually be able to start the application using:

    docker compose up

---

## 4. MVP Scope

The first release will support:

- CSV files only,
- project creation,
- dataset registration,
- dataset versioning,
- asynchronous processing,
- basic data-quality validation,
- version comparison,
- basic lineage,
- interactive visualization,
- and reproducibility metadata.

---

## 5. Out of Scope for MVP

The following are intentionally excluded from the first release:

- authentication and authorization,
- multi-user permissions,
- Excel/Parquet support,
- machine learning,
- LLM functionality,
- Kubernetes,
- distributed computing,
- workflow orchestration platforms such as Airflow,
- real-time collaborative editing,
- and production cloud infrastructure.

These features may be considered later if justified by actual requirements.