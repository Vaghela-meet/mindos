from datetime import time
from typing import List, Optional
from sqlalchemy import case
from sqlalchemy.orm import Session
from app.models.availability import Availability, DayOfWeek
from app.schemas.availability import AvailabilityCreate, AvailabilityUpdate
from app.core.exceptions import (
    AvailabilityNotFoundException,
    AvailabilityValidationException,
    AvailabilityConflictException,
)
from app.core.deps import ensure_dev_user


WEEKDAY_SORT_ORDER = {
    DayOfWeek.MONDAY: 1,
    DayOfWeek.TUESDAY: 2,
    DayOfWeek.WEDNESDAY: 3,
    DayOfWeek.THURSDAY: 4,
    DayOfWeek.FRIDAY: 5,
    DayOfWeek.SATURDAY: 6,
    DayOfWeek.SUNDAY: 7,
}


class AvailabilityService:
    @staticmethod
    def _check_overlap(
        db: Session,
        user_id: int,
        day_of_week: DayOfWeek,
        start_time: time,
        end_time: time,
        exclude_id: Optional[int] = None,
    ) -> None:
        """
        Validates that the requested [start_time, end_time) window does not overlap
        with any existing window for the same user on the specified weekday.
        Touching boundaries (adjacent windows) are permitted.
        """
        query = db.query(Availability).filter(
            Availability.user_id == user_id,
            Availability.day_of_week == day_of_week,
            Availability.start_time < end_time,
            Availability.end_time > start_time,
        )
        if exclude_id is not None:
            query = query.filter(Availability.id != exclude_id)

        conflict = query.first()
        if conflict:
            raise AvailabilityConflictException(
                f"Availability window ({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}) "
                f"overlaps with existing {day_of_week.value} window "
                f"({conflict.start_time.strftime('%H:%M')} - {conflict.end_time.strftime('%H:%M')})."
            )

    @staticmethod
    def create_availability(
        db: Session,
        availability_in: AvailabilityCreate,
        user_id: int,
    ) -> Availability:
        """
        Create a new weekly availability window for the user.
        Enforces user existence, start < end, and non-overlapping window constraints.
        """
        ensure_dev_user(db, user_id)

        if availability_in.start_time >= availability_in.end_time:
            raise AvailabilityValidationException(
                "start_time must be strictly before end_time (zero or negative duration is invalid)"
            )

        AvailabilityService._check_overlap(
            db=db,
            user_id=user_id,
            day_of_week=availability_in.day_of_week,
            start_time=availability_in.start_time,
            end_time=availability_in.end_time,
        )

        availability = Availability(
            user_id=user_id,
            day_of_week=availability_in.day_of_week,
            start_time=availability_in.start_time,
            end_time=availability_in.end_time,
        )
        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability

    @staticmethod
    def get_availabilities(
        db: Session,
        user_id: int,
        day_of_week: Optional[DayOfWeek] = None,
    ) -> List[Availability]:
        """
        List all availability windows for the user, ordered by day of week (Mon-Sun)
        and start time ascending. Optionally filtered by a specific weekday.
        """
        query = db.query(Availability).filter(Availability.user_id == user_id)
        if day_of_week is not None:
            query = query.filter(Availability.day_of_week == day_of_week)

        weekday_case = case(
            WEEKDAY_SORT_ORDER,
            value=Availability.day_of_week,
        )
        return query.order_by(weekday_case, Availability.start_time.asc()).all()

    @staticmethod
    def get_availability(
        db: Session,
        availability_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[Availability]:
        """Fetch a single availability window by ID, scoped to user if provided."""
        query = db.query(Availability).filter(Availability.id == availability_id)
        if user_id is not None:
            query = query.filter(Availability.user_id == user_id)
        return query.first()

    @staticmethod
    def update_availability(
        db: Session,
        availability_id: int,
        availability_in: AvailabilityUpdate,
        user_id: Optional[int] = None,
    ) -> Availability:
        """
        Update an existing availability window.
        Preserves all validation rules: start < end and overlap checks against existing windows.
        """
        availability = AvailabilityService.get_availability(db, availability_id, user_id)
        if not availability:
            raise AvailabilityNotFoundException(f"Availability with id {availability_id} not found")

        target_day = availability_in.day_of_week or availability.day_of_week
        target_start = availability_in.start_time or availability.start_time
        target_end = availability_in.end_time or availability.end_time

        if target_start >= target_end:
            raise AvailabilityValidationException(
                "start_time must be strictly before end_time (zero or negative duration is invalid)"
            )

        # Check overlap excluding the record currently being modified
        AvailabilityService._check_overlap(
            db=db,
            user_id=availability.user_id,
            day_of_week=target_day,
            start_time=target_start,
            end_time=target_end,
            exclude_id=availability.id,
        )

        if availability_in.day_of_week is not None:
            availability.day_of_week = availability_in.day_of_week
        if availability_in.start_time is not None:
            availability.start_time = availability_in.start_time
        if availability_in.end_time is not None:
            availability.end_time = availability_in.end_time

        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability

    @staticmethod
    def delete_availability(
        db: Session,
        availability_id: int,
        user_id: Optional[int] = None,
    ) -> None:
        """Delete an availability window."""
        availability = AvailabilityService.get_availability(db, availability_id, user_id)
        if not availability:
            raise AvailabilityNotFoundException(f"Availability with id {availability_id} not found")

        db.delete(availability)
        db.commit()
