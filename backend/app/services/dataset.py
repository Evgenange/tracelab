import hashlib
import uuid
from pathlib import Path

from app.core.queue import get_queue
from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion
from app.repositories.dataset import DatasetRepository
from app.repositories.job import JobRepository
from app.schemas.dataset import DatasetCreate
from app.services.storage import LocalStorageService
from app.workers.tasks import process_dataset_version


class DatasetNotFoundError(Exception):
    pass


class DuplicateDatasetVersionError(Exception):
    pass


class InvalidDatasetFileError(Exception):
    pass


class DatasetService:
    def __init__(
        self,
        repository: DatasetRepository,
        job_repository: JobRepository,
        storage: LocalStorageService,
    ) -> None:
        self.repository = repository
        self.job_repository = job_repository
        self.storage = storage

    def create_dataset(
        self,
        *,
        project_id: uuid.UUID,
        data: DatasetCreate,
    ) -> Dataset:
        return self.repository.create_dataset(
            project_id=project_id,
            name=data.name,
            description=data.description,
        )

    def list_datasets(
        self,
        project_id: uuid.UUID,
    ) -> list[Dataset]:
        return self.repository.list_for_project(project_id)

    def upload_version(
        self,
        *,
        dataset_id: uuid.UUID,
        filename: str,
        content: bytes,
    ) -> DatasetVersion:
        dataset = self.repository.get_dataset(dataset_id)

        if dataset is None:
            raise DatasetNotFoundError

        if not filename.lower().endswith(".csv"):
            raise InvalidDatasetFileError("Only CSV files are supported.")

        if not content:
            raise InvalidDatasetFileError("Uploaded file is empty.")

        checksum = hashlib.sha256(content).hexdigest()

        existing = self.repository.get_version_by_hash(
            dataset_id=dataset_id,
            sha256=checksum,
        )

        if existing is not None:
            raise DuplicateDatasetVersionError("This exact file already exists for this dataset.")

        version_number = self.repository.get_next_version_number(dataset_id)

        version_id = uuid.uuid4()

        storage_path, stored_checksum = self.storage.save_dataset_version(
            dataset_id=dataset_id,
            version_id=version_id,
            filename=Path(filename).name,
            content=content,
        )

        if checksum != stored_checksum:
            raise RuntimeError("Stored file checksum does not match uploaded content.")

        version = self.repository.create_version(
            version_id=version_id,
            dataset_id=dataset_id,
            version_number=version_number,
            original_filename=Path(filename).name,
            storage_path=storage_path,
            sha256=checksum,
            file_size_bytes=len(content),
        )
        job = self.job_repository.create_job(version.id)
        queue = get_queue()

        queue.enqueue(
            process_dataset_version,
            str(job.id),
            str(version.id),
        )

        return version

    def list_versions(
        self,
        dataset_id: uuid.UUID,
    ) -> list[DatasetVersion]:
        dataset = self.repository.get_dataset(dataset_id)

        if dataset is None:
            raise DatasetNotFoundError

        return self.repository.list_versions(dataset_id)
