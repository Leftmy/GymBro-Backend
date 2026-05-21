"""Domain exceptions for workout service layer."""


class WorkoutException(Exception):
    """Base exception for workout-related errors."""

    pass


class WorkoutNotFoundError(WorkoutException):
    """Raised when a requested workout is not found."""

    def __init__(self, workout_id: int):
        self.workout_id = workout_id
        super().__init__(f"Workout with ID {workout_id} not found")


class WorkoutAlreadyExistsError(WorkoutException):
    """Raised when attempting to create a workout with duplicate name."""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Workout with name '{name}' already exists for this user")


class InvalidExercisesError(WorkoutException):
    """Raised when exercise list validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Invalid exercises: {message}")


class ExerciseNotFoundError(WorkoutException):
    """Raised when an exercise in a workout plan is not found."""

    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"Exercise with slug '{slug}' not found")


class UserWorkoutPlanNotFoundError(WorkoutException):
    """Raised when a user workout plan assignment is not found."""

    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        super().__init__(f"User workout plan with ID {plan_id} not found")


class InvalidDayError(WorkoutException):
    """Raised when an invalid day value is provided."""

    def __init__(self, day: str):
        self.day = day
        super().__init__(
            f"Invalid day '{day}'. Must be a day name (Mon-Sun) or number (1-7)"
        )
