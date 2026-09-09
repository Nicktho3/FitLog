"""Request validation and safe response shapes."""
from datetime import date as Date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Name = Annotated[str, Field(min_length=1, max_length=120)]
Amount = Annotated[float, Field(ge=0, le=100000, allow_inf_nan=False)]


class Input(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class UserLogin(Input):
    email: str = Field(min_length=3, max_length=254, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    password: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()



class UserCreate(UserLogin):
    username: str = Field(min_length=2, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    username: str


class FoodCreate(Input):
    date: Date
    name: Name
    calories: Amount
    protein: Amount = 0
    carbs: Amount = 0
    fat: Amount = 0


class FoodResponse(FoodCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class WorkoutCreate(Input):
    date: Date
    exercise: Name
    sets: int = Field(ge=1, le=100)
    reps: int = Field(ge=1, le=1000)
    weight: Amount = 0


class WorkoutResponse(WorkoutCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class GoalInput(Input):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    calories: float = Field(gt=0, le=100000, allow_inf_nan=False)
    protein: Amount
    carbs: Amount
    fat: Amount
