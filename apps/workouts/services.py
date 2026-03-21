from django.db import transaction
from apps.users.models import User
from .models.workout_plan import WorkoutPlan
from .models.workout_plan_exercise import WorkoutPlanExercise
from apps.exercises.models import Exercise


class WorkoutService:

    @staticmethod
    def get_all_user_workouts(user: User):
        return WorkoutPlan.objects.filter(created_by=user)

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