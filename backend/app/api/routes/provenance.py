import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.dataset import DatasetRepository
from app.repositories.job import JobRepository
from app.schemas.provenance import ProvenanceRead

router = APIRouter()


@router.get(
    "/dataset-versions/{version_id}/provenance",
    response_model=ProvenanceRead,
)
def get_provenance(
    version_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ProvenanceRead:
    dataset_repository = DatasetRepository(db)
    job_repository = JobRepository(db)

    version = dataset_repository.get_version(version_id)

    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset version not found",
        )

    job = job_repository.get_latest_for_version(version_id)
    quality_report = job_repository.get_quality_report(version_id)

    return ProvenanceRead(
        dataset_version_id=version.id,
        dataset_id=version.dataset_id,
        version_number=version.version_number,
        original_filename=version.original_filename,
        sha256=version.sha256,
        file_size_bytes=version.file_size_bytes,
        version_status=version.status,
        version_created_at=version.created_at,
        processing_job_id=job.id if job else None,
        processing_status=job.status if job else None,
        processing_started_at=job.started_at if job else None,
        processing_completed_at=job.completed_at if job else None,
        quality_report_id=(quality_report.id if quality_report else None),
        quality_report_created_at=(quality_report.created_at if quality_report else None),
    )
