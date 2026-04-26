from django.db import transaction
from apps.users.models import User
from apps.workouts.models.user_workout_plan import UserWorkoutPlan
from .models.workout_plan import WorkoutPlan
from .models.workout_plan_exercise import WorkoutPlanExercise
from apps.exercises.models import Exercise

DAY_MAP = {
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5,
        "saturday": 6,
        "sunday": 7,
    }
class WorkoutService:
    @staticmethod
    def get_all_user_workouts(user: User):
        return UserWorkoutPlan.objects.filter(user=user)

    @staticmethod
    def filter_user_workouts_by_day(workouts, day: str):
        if day and day != "all":
            day = DAY_MAP.get(day.lower(), day)

            try:
                day = int(day)
            except ValueError:
                raise ValueError("Invalid day")

            workouts = workouts.filter(day_of_week=day)

            workouts = workouts.filter(day_of_week=day)

        return workouts

    @staticmethod
    def get_workout_by_name(name: str, user: User = None):
        qs = WorkoutPlan.objects.filter(name=name)
        if user:
            qs = qs.filter(created_by=user)
        return qs.first()

    @staticmethod
    def get_workout_by_id(wrkt_id: int):
        return WorkoutPlan.objects.filter(pk=wrkt_id).first()


    @staticmethod
    def create_workout(
        *,
        name: str,
        description: str = "",
        created_by: User,
        public: bool = False,
        exercises: list[dict],
    ):
        if WorkoutPlan.objects.filter(name=name, created_by=created_by).exists():
            return None

        WorkoutService._validate_exercises(exercises)

        with transaction.atomic():
            workout = WorkoutPlan.objects.create(
                name=name,
                description=description,
                created_by=created_by,
                is_public=public,
            )

            plan_exercises = WorkoutService._build_plan_exercises(
                workout, exercises
            )

            WorkoutPlanExercise.objects.bulk_create(plan_exercises)

            return workout


    @staticmethod
    def update_workout(wrkt_id: int, **data):
        workout = WorkoutService.get_workout_by_id(wrkt_id)
        if not workout:
            return None

        exercises = data.pop("exercises", None)

        allowed_fields = {"name", "description", "is_public"}

        with transaction.atomic():
            for attr, value in data.items():
                if attr in allowed_fields:
                    setattr(workout, attr, value)

            workout.save()

            if exercises is not None:
                WorkoutService._validate_exercises(exercises)

                workout.plan_exercises.all().delete()

                plan_exercises = WorkoutService._build_plan_exercises(
                    workout, exercises
                )

                WorkoutPlanExercise.objects.bulk_create(plan_exercises)

            return workout


    @staticmethod
    def delete_workout(wrkt_id: int):
        deleted, _ = WorkoutPlan.objects.filter(pk=wrkt_id).delete()
        return deleted > 0


    @staticmethod
    def _validate_exercises(exercises: list[dict]):
        if not exercises:
            return

        orders = [item.get("order") for item in exercises]

        if None in orders:
            raise ValueError("Each exercise must have an 'order'")

        if len(orders) != len(set(orders)):
            raise ValueError("Order values must be unique within a workout")

    @staticmethod
    def _build_plan_exercises(workout, exercises: list[dict]):
        slugs = [item["slug"] for item in exercises]

        exercise_map = {
            e.slug: e for e in Exercise.objects.filter(slug__in=slugs)
        }

        result = []

        for item in exercises:
            exercise = exercise_map.get(item["slug"])
            if not exercise:
                continue

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
    
    @staticmethod
    def assign_workout_to_user(*, user, workout_plan_id, day_of_week=None, is_active=True):
        workout = WorkoutPlan.objects.filter(id=workout_plan_id).first()
        if not workout:
            return None

        with transaction.atomic():
            # 🔹 only one active
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
    def update_user_workout_plan(instance, **data):
        with transaction.atomic():
            if data.get("is_active"):
                UserWorkoutPlan.objects.filter(
                    user=instance.user,
                    is_active=True
                ).exclude(pk=instance.pk).update(is_active=False)

            for attr in ["day_of_week", "is_active"]:
                if attr in data:
                    setattr(instance, attr, data[attr])

            instance.save()
            return instance