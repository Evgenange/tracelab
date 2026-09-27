import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.dataset_version import DatasetVersion


class DatasetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_dataset(
        self,
        *,
        project_id: uuid.UUID,
        name: str,
        description: str | None,
    ) -> Dataset:
        dataset = Dataset(
            project_id=project_id,
            name=name,
            description=description,
        )

        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)

        return dataset

    def list_for_project(
        self,
        project_id: uuid.UUID,
    ) -> list[Dataset]:
        statement = (
            select(Dataset)
            .where(Dataset.project_id == project_id)
            .order_by(Dataset.created_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_dataset(
        self,
        dataset_id: uuid.UUID,
    ) -> Dataset | None:
        return self.db.get(Dataset, dataset_id)

    def get_version_by_hash(
        self,
        *,
        dataset_id: uuid.UUID,
        sha256: str,
    ) -> DatasetVersion | None:
        statement = select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.sha256 == sha256,
        )

        return self.db.scalar(statement)

    def get_next_version_number(
        self,
        dataset_id: uuid.UUID,
    ) -> int:
        statement = select(func.max(DatasetVersion.version_number)).where(
            DatasetVersion.dataset_id == dataset_id
        )

        current_version = self.db.scalar(statement)

        return (current_version or 0) + 1

    def create_version(
        self,
        *,
        version_id: uuid.UUID,
        dataset_id: uuid.UUID,
        version_number: int,
        original_filename: str,
        storage_path: str,
        sha256: str,
        file_size_bytes: int,
    ) -> DatasetVersion:
        version = DatasetVersion(
            id=version_id,
            dataset_id=dataset_id,
            version_number=version_number,
            original_filename=original_filename,
            storage_path=storage_path,
            sha256=sha256,
            file_size_bytes=file_size_bytes,
            status="uploaded",
        )

        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)

        return version

    def list_versions(
        self,
        dataset_id: uuid.UUID,
    ) -> list[DatasetVersion]:
        statement = (
            select(DatasetVersion)
            .where(DatasetVersion.dataset_id == dataset_id)
            .order_by(DatasetVersion.version_number.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_version(
        self,
        version_id: uuid.UUID,
    ) -> DatasetVersion | None:
        return self.db.get(
            DatasetVersion,
            version_id,
        )
