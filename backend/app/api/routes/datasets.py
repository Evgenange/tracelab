import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.api.dependencies import get_dataset_service
from app.schemas.dataset import (
    DatasetCreate,
    DatasetRead,
    DatasetVersionRead,
)
from app.services.dataset import (
    DatasetNotFoundError,
    DatasetService,
    DuplicateDatasetVersionError,
    InvalidDatasetFileError,
)

router = APIRouter()


@router.post(
    "/projects/{project_id}/datasets",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_dataset(
    project_id: uuid.UUID,
    data: DatasetCreate,
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetRead:
    dataset = service.create_dataset(
        project_id=project_id,
        data=data,
    )

    return DatasetRead.model_validate(dataset)


@router.get(
    "/projects/{project_id}/datasets",
    response_model=list[DatasetRead],
)
def list_datasets(
    project_id: uuid.UUID,
    service: DatasetService = Depends(get_dataset_service),
) -> list[DatasetRead]:
    datasets = service.list_datasets(project_id)

    return [DatasetRead.model_validate(dataset) for dataset in datasets]


@router.post(
    "/datasets/{dataset_id}/versions",
    response_model=DatasetVersionRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset_version(
    dataset_id: uuid.UUID,
    file: UploadFile = File(...),
    service: DatasetService = Depends(get_dataset_service),
) -> DatasetVersionRead:
    filename = file.filename or "upload.csv"

    content = await file.read()

    try:
        version = service.upload_version(
            dataset_id=dataset_id,
            filename=filename,
            content=content,
        )

    except DatasetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        ) from exc

    except DuplicateDatasetVersionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except InvalidDatasetFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return DatasetVersionRead.model_validate(version)


@router.get(
    "/datasets/{dataset_id}/versions",
    response_model=list[DatasetVersionRead],
)
def list_dataset_versions(
    dataset_id: uuid.UUID,
    service: DatasetService = Depends(get_dataset_service),
) -> list[DatasetVersionRead]:
    try:
        versions = service.list_versions(dataset_id)

    except DatasetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        ) from exc

    return [DatasetVersionRead.model_validate(version) for version in versions]
