from fastapi import APIRouter
from app.api.v1.endpoints import health, goals, tasks, availability, plans

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(goals.router)
api_router.include_router(tasks.router)
api_router.include_router(availability.router)
api_router.include_router(plans.router)
