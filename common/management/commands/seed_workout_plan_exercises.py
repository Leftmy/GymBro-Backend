import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.exercises.models import Exercise
from apps.workouts.models import (
    WorkoutPlan,
    WorkoutPlanExercise,
)


class Command(BaseCommand):
    help = "Seed workout plan exercises"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing workout plan exercises before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_path = (
            Path(__file__).resolve().parents[2]
            / "fixtures"
            / "workout_plan_exercises.json"
        )

        if not fixture_path.exists():
            self.stdout.write(self.style.ERROR(f"Fixture not found: {fixture_path}"))
            return

        if options["flush"]:
            WorkoutPlanExercise.objects.all().delete()

            self.stdout.write(
                self.style.WARNING("Existing workout plan exercises deleted.")
            )

        with open(fixture_path, encoding="utf-8") as file:
            items = json.load(file)

        created_count = 0

        for item in items:
            workout_plan_name = item.get("workout_plan")
            exercise_name = item.get("exercise")

            try:
                workout_plan = WorkoutPlan.objects.get(name=workout_plan_name)

            except WorkoutPlan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Workout plan not found: {workout_plan_name}")
                )
                continue

            try:
                exercise = Exercise.objects.get(name=exercise_name)

            except Exercise.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Exercise not found: {exercise_name}")
                )
                continue

            _, created = WorkoutPlanExercise.objects.get_or_create(
                workout_plan=workout_plan,
                order=item["order"],
                defaults={
                    "exercise": exercise,
                    "sets": item["sets"],
                    "reps": item["reps"],
                    "rest_seconds": item.get(
                        "rest_seconds",
                        60,
                    ),
                },
            )

            if created:
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(f"Added {exercise.name} to {workout_plan.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Order {item['order']} already exists in {workout_plan.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_count} workout plan exercises."
            )
        )
