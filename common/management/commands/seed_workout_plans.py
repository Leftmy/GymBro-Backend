import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.workouts.models import WorkoutPlan

User = get_user_model()


class Command(BaseCommand):
    help = "Seed workout plans from JSON fixture"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing workout plans before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "fixtures"
            / "workout_plans.json"
        )

        if not fixture_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Fixture not found: {fixture_path}"
                )
            )
            return

        if options["flush"]:
            WorkoutPlan.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    "Existing workout plans deleted."
                )
            )

        with open(fixture_path, "r", encoding="utf-8") as file:
            plans = json.load(file)

        created_count = 0

        for item in plans:
            created_by = None

            username = item.get("created_by")

            if username:
                try:
                    created_by = User.objects.get(
                        username=username
                    )

                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"User not found: {username}"
                        )
                    )
                    continue

            workout_plan, created = WorkoutPlan.objects.get_or_create(
                name=item["name"],
                created_by=created_by,
                defaults={
                    "description": item.get(
                        "description",
                        "",
                    ),
                    "is_public": item.get(
                        "is_public",
                        False,
                    ),
                },
            )

            if created:
                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created workout plan: "
                        f"{workout_plan.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Workout plan already exists: "
                        f"{workout_plan.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created "
                f"{created_count} workout plans."
            )
        )