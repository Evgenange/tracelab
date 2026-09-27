import uuid
from datetime import datetime

from pydantic import BaseModel


class ProvenanceRead(BaseModel):
    dataset_version_id: uuid.UUID
    dataset_id: uuid.UUID
    version_number: int

    original_filename: str
    sha256: str
    file_size_bytes: int

    version_status: str
    version_created_at: datetime

    processing_job_id: uuid.UUID | None = None
    processing_status: str | None = None
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None

    quality_report_id: uuid.UUID | None = None
    quality_report_created_at: datetime | None = None

    pipeline_name: str = "tracelab-csv-profiler"
    pipeline_version: str = "0.1.0"
