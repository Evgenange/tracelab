import uuid
from pathlib import Path

import pandas as pd

from app.db.session import SessionLocal
from app.models.dataset_version import DatasetVersion
from app.models.processing_job import ProcessingJob
from app.models.quality_report import QualityReport
from app.repositories.job import JobRepository


def process_dataset_version(
    job_id: str,
    dataset_version_id: str,
) -> None:
    db = SessionLocal()

    try:
        job_uuid = uuid.UUID(job_id)
        version_uuid = uuid.UUID(dataset_version_id)

        repository = JobRepository(db)

        job = repository.get_job(job_uuid)

        if job is None:
            raise RuntimeError(f"Processing job {job_id} does not exist.")

        repository.mark_processing(job)

        version = db.get(
            DatasetVersion,
            version_uuid,
        )

        if version is None:
            raise RuntimeError(f"Dataset version {dataset_version_id} does not exist.")

        version.status = "processing"
        db.commit()

        file_path = Path(version.storage_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")

        dataframe = pd.read_csv(file_path)

        row_count = len(dataframe)
        column_count = len(dataframe.columns)

        duplicate_row_count = int(dataframe.duplicated().sum())

        null_counts = {
            str(column): int(count) for column, count in dataframe.isnull().sum().items()
        }

        null_count = sum(null_counts.values())

        schema = {str(column): str(dtype) for column, dtype in dataframe.dtypes.items()}

        numeric_dataframe = dataframe.select_dtypes(include="number")

        numeric_summary: dict[str, dict[str, float | None]] = {}

        for column in numeric_dataframe.columns:
            series = numeric_dataframe[column]

            numeric_summary[str(column)] = {
                "min": (float(series.min()) if not series.empty else None),
                "max": (float(series.max()) if not series.empty else None),
                "mean": (float(series.mean()) if not series.empty else None),
                "median": (float(series.median()) if not series.empty else None),
            }

        report = QualityReport(
            dataset_version_id=version_uuid,
            row_count=row_count,
            column_count=column_count,
            duplicate_row_count=duplicate_row_count,
            null_count=null_count,
            schema_json=schema,
            null_counts_json=null_counts,
            numeric_summary_json=numeric_summary,
        )

        repository.save_quality_report(report)

        version.status = "completed"
        db.commit()

        repository.mark_completed(job)

    except Exception as exc:
        db.rollback()

        job = db.get(
            ProcessingJob,
            uuid.UUID(job_id),
        )

        if job is not None:
            job.status = "failed"
            job.error_message = str(exc)
            job.completed_at = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            )

            db.commit()

        version = db.get(
            DatasetVersion,
            uuid.UUID(dataset_version_id),
        )

        if version is not None:
            version.status = "failed"
            db.commit()

        raise

    finally:
        db.close()
