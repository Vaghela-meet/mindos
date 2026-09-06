from typing import Optional
from pydantic import BaseModel


class DatabaseStatus(BaseModel):
    status: str
    database: str
    detail: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    app: str
    version: str
    environment: str
    database: DatabaseStatus
