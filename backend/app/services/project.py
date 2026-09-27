import uuid

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepository,
    ) -> None:
        self.repository = repository

    def create_project(
        self,
        data: ProjectCreate,
    ) -> Project:
        return self.repository.create(
            name=data.name,
            description=data.description,
        )

    def list_projects(self) -> list[Project]:
        return self.repository.list_all()

    def get_project(
        self,
        project_id: uuid.UUID,
    ) -> Project | None:
        return self.repository.get_by_id(project_id)
