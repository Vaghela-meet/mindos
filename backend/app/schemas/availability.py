from datetime import time, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.availability import DayOfWeek


class AvailabilityBase(BaseModel):
    day_of_week: DayOfWeek = Field(..., description="Day of the week (MONDAY-SUNDAY)")
    start_time: time = Field(..., description="Start time of the availability window (e.g. 09:00)")
    end_time: time = Field(..., description="End time of the availability window (e.g. 17:00)")


class AvailabilityCreate(AvailabilityBase):
    @model_validator(mode="after")
    def validate_time_range(self) -> "AvailabilityCreate":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be strictly before end_time (zero or negative duration is invalid)")
        return self


class AvailabilityUpdate(BaseModel):
    day_of_week: Optional[DayOfWeek] = Field(None, description="Day of the week (MONDAY-SUNDAY)")
    start_time: Optional[time] = Field(None, description="Updated start time")
    end_time: Optional[time] = Field(None, description="Updated end time")

    @model_validator(mode="after")
    def validate_time_range(self) -> "AvailabilityUpdate":
        if self.start_time is not None and self.end_time is not None:
            if self.start_time >= self.end_time:
                raise ValueError("start_time must be strictly before end_time (zero or negative duration is invalid)")
        return self


class AvailabilityResponse(AvailabilityBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
