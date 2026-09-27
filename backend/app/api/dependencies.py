from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.dataset import DatasetRepository
from app.repositories.job import JobRepository
from app.repositories.project import ProjectRepository
from app.services.dataset import DatasetService
from app.services.project import ProjectService
from app.services.storage import LocalStorageService


def get_project_service(
    db: Session = Depends(get_db),
) -> ProjectService:
    repository = ProjectRepository(db)

    return ProjectService(
        repository=repository,
    )


def get_dataset_service(
    db: Session = Depends(get_db),
) -> DatasetService:
    settings = get_settings()

    dataset_repository = DatasetRepository(db)
    job_repository = JobRepository(db)

    storage = LocalStorageService(settings.storage_path)

    return DatasetService(
        repository=dataset_repository,
        job_repository=job_repository,
        storage=storage,
    )
