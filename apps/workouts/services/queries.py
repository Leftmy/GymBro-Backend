from typing import Optional, List
from django.db.models import QuerySet
from apps.users.models import User
from apps.workouts.models.user_workout_plan import UserWorkoutPlan
from apps.workouts.models.workout_plan import WorkoutPlan
from .exceptions import InvalidDayError


class WorkoutQueries:
    """Read-only operations for workout queries with optimized database access."""

    # Day mapping for easy conversion
    DAY_MAP = {
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5,
        "saturday": 6,
        "sunday": 7,
    }

    @staticmethod
    def get_all_user_workouts(current_user: User, user_uuid: Optional[str] = None) -> QuerySet[UserWorkoutPlan]:
        """
        Fetch all workouts assigned to a user with optimized queries.
        
        Args:
            current_user: The User instance making the request
            user_uuid: Optional UUID of the user to fetch workouts for. If provided, returns only public workouts.
            
        Returns:
            QuerySet of UserWorkoutPlan instances
        """
        if user_uuid:
            qs = UserWorkoutPlan.objects.filter(user__uuid=user_uuid, workout_plan__is_public=True)
        else:
            qs = UserWorkoutPlan.objects.filter(user=current_user)
            
        return (
            qs
            .select_related("workout_plan", "user")
            .prefetch_related("workout_plan__plan_exercises__exercise")
        )

    @staticmethod
    def filter_user_workouts_by_day(
        workouts: QuerySet, day: Optional[str] = None
    ) -> QuerySet[UserWorkoutPlan]:
        """
        Filter workouts by day of week.
        
        Args:
            workouts: QuerySet of workouts to filter
            day: Day name or number (case-insensitive). None or 'all' returns all workouts
            
        Returns:
            Filtered QuerySet
            
        Raises:
            InvalidDayError: If day is invalid
        """
        if day is None:
            return workouts

        day_normalized = str(day).strip().lower() 
        
        if not day_normalized or day_normalized == "all":
            return workouts

        # Try to convert day name to number
        day_value = WorkoutQueries.DAY_MAP.get(day_normalized)
        
        if day_value is None:
            try:
                day_value = int(day_normalized)
                if not 1 <= day_value <= 7:
                    raise InvalidDayError(day)
            except (ValueError, TypeError):
                raise InvalidDayError(day)

        return workouts.filter(day_of_week=day_value)

    @staticmethod
    def get_workout_by_name(
        name: str, user: Optional[User] = None
    ) -> Optional[WorkoutPlan]:
        """
        Retrieve a workout by name.
        
        Args:
            name: Workout name
            user: Optional User filter (owner of the workout)
            
        Returns:
            WorkoutPlan instance or None
        """
        qs = WorkoutPlan.objects.filter(name=name).select_related("created_by")
        
        if user:
            qs = qs.filter(created_by=user)
        
        return qs.prefetch_related("plan_exercises__exercise").first()

    @staticmethod
    def get_workout_by_id(workout_id: int) -> Optional[WorkoutPlan]:
        """
        Retrieve a workout by ID with related exercises.
        
        Args:
            workout_id: Primary key of the workout
            
        Returns:
            WorkoutPlan instance or None
        """
        return (
            WorkoutPlan.objects.filter(pk=workout_id)
            .select_related("created_by")
            .prefetch_related("plan_exercises__exercise")
            .first()
        )

    @staticmethod
    def get_user_active_workout(user: User) -> Optional[UserWorkoutPlan]:
        """
        Get the currently active workout for a user.
        
        Args:
            user: The User instance
            
        Returns:
            Active UserWorkoutPlan or None
        """
        return (
            UserWorkoutPlan.objects.filter(user=user, is_active=True)
            .select_related("workout_plan", "user")
            .prefetch_related("workout_plan__plan_exercises__exercise")
            .first()
        )

    @staticmethod
    def get_user_workout_plan(user_workout_plan_id: int) -> Optional[UserWorkoutPlan]:
        """
        Get a specific user workout plan with all related data.
        
        Args:
            user_workout_plan_id: Primary key of the UserWorkoutPlan
            
        Returns:
            UserWorkoutPlan instance or None
        """
        return (
            UserWorkoutPlan.objects.filter(pk=user_workout_plan_id)
            .select_related("workout_plan", "user")
            .prefetch_related("workout_plan__plan_exercises__exercise")
            .first()
        )

    @staticmethod
    def check_workout_exists(workout_id: int) -> bool:
        """
        Quick check if a workout exists.
        
        Args:
            workout_id: Primary key of the workout
            
        Returns:
            True if exists, False otherwise
        """
        return WorkoutPlan.objects.filter(pk=workout_id).exists()

    @staticmethod
    def check_user_has_active_workout(user: User) -> bool:
        """
        Check if user has an active workout assigned.
        
        Args:
            user: The User instance
            
        Returns:
            True if user has an active workout
        """
        return UserWorkoutPlan.objects.filter(
            user=user, is_active=True
        ).exists()