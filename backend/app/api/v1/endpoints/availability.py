from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.core.exceptions import (
    AvailabilityNotFoundException,
    AvailabilityValidationException,
    AvailabilityConflictException,
)
from app.models.availability import DayOfWeek
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityUpdate,
    AvailabilityResponse,
)
from app.services.availability.service import AvailabilityService

router = APIRouter(prefix="/availability", tags=["Availability"])


@router.post("", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_availability(
    availability_in: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> AvailabilityResponse:
    """Create a new weekly availability window for the active user."""
    try:
        return AvailabilityService.create_availability(db, availability_in, current_user_id)
    except AvailabilityValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except AvailabilityConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.get("", response_model=List[AvailabilityResponse])
def get_availabilities(
    day_of_week: Optional[DayOfWeek] = Query(None, alias="day_of_week", description="Filter by weekday"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> List[AvailabilityResponse]:
    """List all availability windows for the active user, optionally filtered by weekday."""
    return AvailabilityService.get_availabilities(db, current_user_id, day_of_week=day_of_week)


@router.get("/{availability_id}", response_model=AvailabilityResponse)
def get_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> AvailabilityResponse:
    """Retrieve a specific availability window by ID."""
    availability = AvailabilityService.get_availability(db, availability_id, user_id=current_user_id)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Availability with id {availability_id} not found",
        )
    return availability


@router.patch("/{availability_id}", response_model=AvailabilityResponse)
def update_availability(
    availability_id: int,
    availability_in: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> AvailabilityResponse:
    """Update attributes of an existing availability window."""
    try:
        return AvailabilityService.update_availability(
            db, availability_id, availability_in, user_id=current_user_id
        )
    except AvailabilityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except AvailabilityValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except AvailabilityConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> None:
    """Delete an availability window."""
    try:
        AvailabilityService.delete_availability(db, availability_id, user_id=current_user_id)
    except AvailabilityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
