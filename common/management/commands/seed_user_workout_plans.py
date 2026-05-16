import json
from pathlib import Path
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.workouts.models import (
    UserWorkoutPlan,
    WorkoutPlan,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed user workout plans"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing user workout plans before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "fixtures"
            / "user_workout_plans.json"
        )

        if not fixture_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Fixture not found: {fixture_path}"
                )
            )
            return

        if options["flush"]:
            UserWorkoutPlan.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    "Existing user workout plans deleted."
                )
            )

        with open(fixture_path, "r", encoding="utf-8") as file:
            items = json.load(file)

        created_count = 0

        for item in items:
            username = item.get("username")
            workout_plan_name = item.get("workout_plan")

            try:
                user = User.objects.get(username=username)

            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"User not found: {username}"
                    )
                )
                continue

            try:
                workout_plan = WorkoutPlan.objects.get(
                    name=workout_plan_name
                )

            except WorkoutPlan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Workout plan not found: "
                        f"{workout_plan_name}"
                    )
                )
                continue

            started_at = None

            if item.get("started_at"):
                started_at = datetime.strptime(
                    item["started_at"],
                    "%Y-%m-%d"
                ).date()

            _, created = UserWorkoutPlan.objects.get_or_create(
                user=user,
                workout_plan=workout_plan,
                defaults={
                    "is_active": item.get(
                        "is_active",
                        False,
                    ),
                    "started_at": started_at,
                    "day_of_week": item.get(
                        "day_of_week"
                    ),
                },
            )

            if created:
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Assigned "
                        f"{workout_plan.name} "
                        f"to {user.username}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Plan already assigned: "
                        f"{user.username} -> "
                        f"{workout_plan.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created "
                f"{created_count} user workout plans."
            )
        )