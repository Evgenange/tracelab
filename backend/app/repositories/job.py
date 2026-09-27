import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.processing_job import ProcessingJob
from app.models.quality_report import QualityReport


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_job(
        self,
        dataset_version_id: uuid.UUID,
    ) -> ProcessingJob:
        job = ProcessingJob(
            dataset_version_id=dataset_version_id,
            status="queued",
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_job(
        self,
        job_id: uuid.UUID,
    ) -> ProcessingJob | None:
        return self.db.get(
            ProcessingJob,
            job_id,
        )

    def get_latest_for_version(
        self,
        version_id: uuid.UUID,
    ) -> ProcessingJob | None:
        statement = (
            select(ProcessingJob)
            .where(ProcessingJob.dataset_version_id == version_id)
            .order_by(ProcessingJob.created_at.desc())
        )

        return self.db.scalar(statement)

    def mark_processing(
        self,
        job: ProcessingJob,
    ) -> None:
        job.status = "processing"
        job.started_at = datetime.now(UTC)

        self.db.commit()

    def mark_completed(
        self,
        job: ProcessingJob,
    ) -> None:
        job.status = "completed"
        job.completed_at = datetime.now(UTC)

        self.db.commit()

    def mark_failed(
        self,
        job: ProcessingJob,
        error_message: str,
    ) -> None:
        job.status = "failed"
        job.error_message = error_message
        job.completed_at = datetime.now(UTC)

        self.db.commit()

    def save_quality_report(
        self,
        report: QualityReport,
    ) -> QualityReport:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report

    def get_quality_report(
        self,
        dataset_version_id: uuid.UUID,
    ) -> QualityReport | None:
        statement = select(QualityReport).where(
            QualityReport.dataset_version_id == dataset_version_id
        )

        return self.db.scalar(statement)
