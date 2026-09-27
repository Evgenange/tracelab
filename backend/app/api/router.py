from fastapi import APIRouter

from app.api.routes import datasets, health, jobs, projects, provenance

api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
)

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"],
)

api_router.include_router(
    datasets.router,
    tags=["datasets"],
)

api_router.include_router(
    jobs.router,
    tags=["jobs"],
)

api_router.include_router(
    provenance.router,
    tags=["provenance"],
)
