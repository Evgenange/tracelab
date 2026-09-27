import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        name: str,
        description: str | None,
    ) -> Project:
        project = Project(
            name=name,
            description=description,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def list_all(self) -> list[Project]:
        statement = select(Project).order_by(Project.created_at.desc())

        return list(self.db.scalars(statement).all())

    def get_by_id(
        self,
        project_id: uuid.UUID,
    ) -> Project | None:
        return self.db.get(Project, project_id)
