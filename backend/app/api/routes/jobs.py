import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.job import JobRepository
from app.schemas.job import ProcessingJobRead, QualityReportRead

router = APIRouter(tags=["jobs"])


@router.get(
    "/jobs/{job_id}",
    response_model=ProcessingJobRead,
)
def get_processing_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ProcessingJobRead:
    repository = JobRepository(db)
    job = repository.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing job not found",
        )

    return ProcessingJobRead.model_validate(job)


@router.get(
    "/dataset-versions/{version_id}/quality",
    response_model=QualityReportRead,
)
def get_quality_report(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> QualityReportRead:
    repository = JobRepository(db)
    report = repository.get_quality_report(version_id)

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality report not found",
        )

    return QualityReportRead.model_validate(report)
