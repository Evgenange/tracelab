import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProcessingJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_version_id: uuid.UUID
    status: str
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class QualityReportRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: uuid.UUID
    dataset_version_id: uuid.UUID
    row_count: int
    column_count: int
    duplicate_row_count: int
    null_count: int

    column_schema: dict[str, Any] = Field(
        validation_alias="schema_json",
    )

    null_counts_json: dict[str, Any]
    numeric_summary_json: dict[str, Any]
    created_at: datetime
