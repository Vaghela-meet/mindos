from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_db_connection
from app.schemas.health import HealthCheckResponse, DatabaseStatus

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="MindOS Health Status",
    description="Returns backend service readiness, version info, and database connectivity status.",
)
def get_health() -> HealthCheckResponse:
    db_result = check_db_connection()
    return HealthCheckResponse(
        status="ok",
        app=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=DatabaseStatus(**db_result),
    )
