"""Data Transfer Objects for workout service commands and queries."""

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
    exercises: list[ExerciseDTO] = field(default_factory=list)

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
    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    exercises: list[ExerciseDTO] | None = None

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
    day_of_week: int | None = None
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
    day_of_week: int | None = None
    is_active: bool | None = None

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
    exercises: list[ExerciseDTO] = field(default_factory=list)


@dataclass
class UserWorkoutPlanDTO:
    """DTO for user workout plan assignment response."""

    id: int
    user_id: int
    workout_plan_id: int
    day_of_week: int | None
    is_active: bool
    created_at: datetime
    assigned_workout: WorkoutPlanDTO | None = None


@dataclass
class WorkoutFilterQuery:
    """DTO for filtering workouts."""

    user_id: int
    day: str | None = None
    is_active: bool | None = None
