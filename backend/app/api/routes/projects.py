import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_project_service
from app.schemas.project import ProjectCreate, ProjectRead
from app.services.project import ProjectService

router = APIRouter()


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    project = service.create_project(data)

    return ProjectRead.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectRead],
)
def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectRead]:
    projects = service.list_projects()

    return [ProjectRead.model_validate(project) for project in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
)
def get_project(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return ProjectRead.model_validate(project)
