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
            # support description as a simple string or a dict of localized strings
            raw_desc = item.get("description", "")

            if isinstance(raw_desc, dict):
                description_i18n = raw_desc
                # prefer english as the default text fallback
                description_text = raw_desc.get("en") or next(iter(raw_desc.values()), "")
            else:
                description_text = raw_desc
                description_i18n = {"en": raw_desc} if raw_desc else {}

            exercise, created = Exercise.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": description_text,
                    "description_i18n": description_i18n,
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
                # update existing record with i18n data if it's missing or different
                updated = False

                try:
                    existing_i18n = exercise.description_i18n or {}
                except Exception:
                    existing_i18n = {}

                if existing_i18n != description_i18n:
                    exercise.description_i18n = description_i18n
                    # also update the fallback description text
                    exercise.description = description_text
                    exercise.save()
                    updated = True

                if updated:
                    self.stdout.write(self.style.SUCCESS(f"Updated exercise: {exercise.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Already exists: {exercise.name}"))

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