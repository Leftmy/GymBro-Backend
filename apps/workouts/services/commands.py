from typing import Optional, List, Dict, Any
from django.db import transaction
from apps.users.models import User
from apps.workouts.models.user_workout_plan import UserWorkoutPlan
from apps.workouts.models.workout_plan import WorkoutPlan
from apps.workouts.models.workout_plan_exercise import WorkoutPlanExercise
from apps.exercises.models import Exercise
from .exceptions import (
    WorkoutAlreadyExistsError,
    InvalidExercisesError,
    ExerciseNotFoundError,
    WorkoutNotFoundError,
    UserWorkoutPlanNotFoundError
)


class WorkoutCommands:
    """Write operations (commands) for workout management using CQRS pattern."""

    @staticmethod
    def create_workout(
        *,
        name: str,
        description: str = "",
        created_by: User,
        public: bool = False,
        exercises: List[Dict[str, Any]],
    ) -> WorkoutPlan:
        """
        Create a new workout with exercises.
        
        Args:
            name: Workout name (must be unique per user)
            description: Optional workout description
            created_by: User who created the workout
            public: Whether the workout is public
            exercises: List of exercise dicts with required 'slug', 'order', 
                      and optional 'sets', 'reps', 'rest_seconds'
            
        Returns:
            Created WorkoutPlan instance
            
        Raises:
            WorkoutAlreadyExistsError: If workout with same name exists for user
            InvalidExercisesError: If exercises validation fails
        """
        # Check for duplicate name
        if WorkoutPlan.objects.filter(name=name, created_by=created_by).exists():
            raise WorkoutAlreadyExistsError(name)

        WorkoutCommands._validate_exercises(exercises)

        with transaction.atomic():
            workout = WorkoutPlan.objects.create(
                name=name,
                description=description,
                created_by=created_by,
                is_public=public,
            )

            plan_exercises = WorkoutCommands._build_plan_exercises(
                workout, exercises
            )

            if plan_exercises:
                WorkoutPlanExercise.objects.bulk_create(plan_exercises)

            return workout

    @staticmethod
    def update_workout(
        workout_id: int,
        **data: Any
    ) -> WorkoutPlan:
        """
        Update an existing workout and/or its exercises.
        
        Args:
            workout_id: Primary key of the workout to update
            **data: Fields to update (name, description, is_public, exercises)
            
        Returns:
            Updated WorkoutPlan instance
            
        Raises:
            WorkoutNotFoundError: If workout not found
            InvalidExercisesError: If exercises validation fails
        """
        workout = WorkoutPlan.objects.filter(pk=workout_id).first()
        if not workout:
            raise WorkoutNotFoundError(workout_id)

        exercises = data.pop("exercises", None)
        allowed_fields = {"name", "description", "is_public"}

        with transaction.atomic():
            # Update allowed fields
            for attr, value in data.items():
                if attr in allowed_fields:
                    setattr(workout, attr, value)

            workout.save()

            # Update exercises if provided
            if exercises is not None:
                WorkoutCommands._validate_exercises(exercises)
                
                # Delete old exercises and create new ones
                workout.plan_exercises.all().delete()
                
                plan_exercises = WorkoutCommands._build_plan_exercises(
                    workout, exercises
                )
                
                if plan_exercises:
                    WorkoutPlanExercise.objects.bulk_create(plan_exercises)

            return workout

    @staticmethod
    def delete_workout(workout_id: int) -> bool:
        """
        Delete a workout and all associated exercises.
        
        Args:
            workout_id: Primary key of the workout to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        deleted_count, _ = WorkoutPlan.objects.filter(pk=workout_id).delete()
        return deleted_count > 0

    @staticmethod
    def assign_workout_to_user(
        *,
        user: User,
        workout_plan_id: int,
        day_of_week: Optional[int] = None,
        is_active: bool = True,
    ) -> UserWorkoutPlan:
        """
        Assign a workout to a user, ensuring only one active workout at a time.
        
        Args:
            user: The User instance
            workout_plan_id: Primary key of the WorkoutPlan to assign
            day_of_week: Optional day of week (1-7)
            is_active: Whether this assignment should be active
            
        Returns:
            Created UserWorkoutPlan instance
            
        Raises:
            WorkoutNotFoundError: If workout not found
        """
        workout = WorkoutPlan.objects.filter(id=workout_plan_id).first()
        if not workout:
            raise WorkoutNotFoundError(workout_plan_id)

        with transaction.atomic():
            # Deactivate other active workouts if this one is being activated
            if is_active:
                UserWorkoutPlan.objects.filter(
                    user=user,
                    is_active=True
                ).update(is_active=False)

            return UserWorkoutPlan.objects.create(
                user=user,
                workout_plan=workout,
                day_of_week=day_of_week,
                is_active=is_active,
            )

    @staticmethod
    def update_user_workout_plan(
        user_workout_plan_id: int,
        **data: Any
    ) -> UserWorkoutPlan:
        """
        Update a user's workout plan assignment.
        
        Args:
            user_workout_plan_id: Primary key of UserWorkoutPlan to update
            **data: Fields to update (day_of_week, is_active)
            
        Returns:
            Updated UserWorkoutPlan instance
            
        Raises:
            WorkoutNotFoundError: If user workout plan not found
        """
        instance = UserWorkoutPlan.objects.filter(pk=user_workout_plan_id).first()
        if not instance:
            raise UserWorkoutPlanNotFoundError(user_workout_plan_id)

        with transaction.atomic():
            # If activating, deactivate other active workouts for this user
            if data.get("is_active"):
                UserWorkoutPlan.objects.filter(
                    user=instance.user,
                    is_active=True
                ).exclude(pk=instance.pk).update(is_active=False)

            # Update allowed fields
            for attr in ["day_of_week", "is_active"]:
                if attr in data:
                    setattr(instance, attr, data[attr])

            instance.save()
            return instance

    @staticmethod
    def deactivate_user_workout(user_workout_plan_id: int) -> bool:
        """
        Deactivate a user's workout plan.
        
        Args:
            user_workout_plan_id: Primary key of UserWorkoutPlan to deactivate
            
        Returns:
            True if successfully deactivated, False if not found
        """
        instance = UserWorkoutPlan.objects.filter(pk=user_workout_plan_id).first()
        if not instance:
            return False

        instance.is_active = False
        instance.save()
        return True

    @staticmethod
    def unassign_workout_from_user(user_workout_plan_id: int) -> bool:
        """
        Unassign a workout from a user (delete the assignment).
        
        Args:
            user_workout_plan_id: Primary key of UserWorkoutPlan to delete
            
        Returns:
            True if successfully deleted, False if not found
        """
        deleted_count, _ = UserWorkoutPlan.objects.filter(
            pk=user_workout_plan_id
        ).delete()
        return deleted_count > 0

    # ===================== Helper Methods =====================

    @staticmethod
    def _validate_exercises(exercises: List[Dict[str, Any]]) -> None:
        """
        Validate exercise list for required fields and constraints.
        
        Args:
            exercises: List of exercise dictionaries
            
        Raises:
            InvalidExercisesError: If validation fails
        """
        if not exercises:
            raise InvalidExercisesError("At least one exercise must be provided")

        # Extract and validate order values
        orders = [item.get("order") for item in exercises]

        if None in orders:
            raise InvalidExercisesError("Each exercise must have an 'order' field")

        if len(orders) != len(set(orders)):
            raise InvalidExercisesError("Exercise order values must be unique within a workout")

        # Validate all exercises have a slug
        slugs = [item.get("slug") for item in exercises]
        if None in slugs:
            raise InvalidExercisesError("Each exercise must have a 'slug' field")

    @staticmethod
    def _build_plan_exercises(
        workout: WorkoutPlan,
        exercises: List[Dict[str, Any]],
    ) -> List[WorkoutPlanExercise]:
        """
        Build WorkoutPlanExercise instances from exercise data.
        
        Only includes exercises that exist in the database.
        
        Args:
            workout: The WorkoutPlan instance
            exercises: List of exercise data dictionaries
            
        Returns:
            List of WorkoutPlanExercise instances ready to be bulk created
        """
        slugs = [item["slug"] for item in exercises]

        # Fetch all exercises in one query and create a mapping
        exercise_map = {
            e.slug: e for e in Exercise.objects.filter(slug__in=slugs)
        }

        result = []

        for item in exercises:
            exercise = exercise_map.get(item["slug"])
            if not exercise:
                # TODO: add a better logging for errors 
                raise ExerciseNotFoundError(item["slug"])

            result.append(
                WorkoutPlanExercise(
                    workout_plan=workout,
                    exercise=exercise,
                    sets=item.get("sets", 0),
                    reps=item.get("reps", 0),
                    rest_seconds=item.get("rest_seconds", 60),
                    order=item["order"],
                )
            )

        return result
