import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.exercises.models import (
    Exercise,
    MuscleGroup,
    ExerciseMuscle,
)


class Command(BaseCommand):
    help = "Seed exercises from JSON fixture"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        fixture_path = (
            Path(__file__)
            .resolve()
            .parents[2]
            / "fixtures"
            / "exercises.json"
        )

        if not fixture_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Fixture not found: {fixture_path}"
                )
            )
            return

        with open(fixture_path, "r", encoding="utf-8") as file:
            exercises = json.load(file)

        created_count = 0

        for item in exercises:
            exercise, created = Exercise.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item.get("description", ""),
                    "difficulty": item.get(
                        "difficulty",
                        Exercise.Difficulty.BEGINNER,
                    ),
                    "equipment": item.get("equipment", ""),
                    "video_url": item.get("video_url", ""),
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created exercise: {exercise.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Already exists: {exercise.name}"
                    )
                )

            for muscle_name in item.get("muscles", []):
                try:
                    muscle = MuscleGroup.objects.get(
                        name=muscle_name
                    )

                    ExerciseMuscle.objects.get_or_create(
                        exercise=exercise,
                        muscle=muscle,
                    )

                except MuscleGroup.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Muscle not found: {muscle_name}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_count} exercises."
            )
        )