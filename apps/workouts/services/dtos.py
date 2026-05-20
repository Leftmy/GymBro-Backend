"""Data Transfer Objects for workout service commands and queries."""

from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExerciseDTO:
    """DTO for exercise data within a workout."""

    slug: str
    order: int
    sets: int = 0
    reps: int = 0
    rest_seconds: int = 60


@dataclass
class CreateWorkoutCommand:
    """Command DTO for creating a workout."""

    name: str
    created_by_id: int
    description: str = ""
    is_public: bool = False
    exercises: List[ExerciseDTO] = field(default_factory=list)

    def validate(self) -> None:
        """Validate command data."""
        if not self.name or not self.name.strip():
            raise ValueError("Workout name is required")

        if not self.exercises:
            raise ValueError("At least one exercise is required")

        # Validate exercises
        orders = [ex.order for ex in self.exercises]
        if len(orders) != len(set(orders)):
            raise ValueError("Exercise order values must be unique")

        for exercise in self.exercises:
            if not exercise.slug:
                raise ValueError("Exercise slug is required")


@dataclass
class UpdateWorkoutCommand:
    """Command DTO for updating a workout."""

    workout_id: int
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    exercises: Optional[List[ExerciseDTO]] = None

    def validate(self) -> None:
        """Validate command data."""
        if self.name is not None and not self.name.strip():
            raise ValueError("Workout name cannot be empty")

        if self.exercises is not None:
            if not self.exercises:
                raise ValueError("Exercises list cannot be empty")

            orders = [ex.order for ex in self.exercises]
            if len(orders) != len(set(orders)):
                raise ValueError("Exercise order values must be unique")


@dataclass
class AssignWorkoutCommand:
    """Command DTO for assigning a workout to a user."""

    user_id: int
    workout_plan_id: int
    day_of_week: Optional[int] = None
    is_active: bool = True

    def validate(self) -> None:
        """Validate command data."""
        if self.day_of_week is not None:
            if not 1 <= self.day_of_week <= 7:
                raise ValueError("Day of week must be between 1 and 7")


@dataclass
class UpdateUserWorkoutPlanCommand:
    """Command DTO for updating user workout plan assignment."""

    user_workout_plan_id: int
    day_of_week: Optional[int] = None
    is_active: Optional[bool] = None

    def validate(self) -> None:
        """Validate command data."""
        if self.day_of_week is not None:
            if not 1 <= self.day_of_week <= 7:
                raise ValueError("Day of week must be between 1 and 7")


# Query DTOs

@dataclass
class WorkoutPlanDTO:
    """DTO for workout plan response."""

    id: int
    name: str
    description: str
    is_public: bool
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    exercises: List[ExerciseDTO] = field(default_factory=list)


@dataclass
class UserWorkoutPlanDTO:
    """DTO for user workout plan assignment response."""

    id: int
    user_id: int
    workout_plan_id: int
    day_of_week: Optional[int]
    is_active: bool
    created_at: datetime
    assigned_workout: Optional[WorkoutPlanDTO] = None


@dataclass
class WorkoutFilterQuery:
    """DTO for filtering workouts."""

    user_id: int
    day: Optional[str] = None
    is_active: Optional[bool] = None
