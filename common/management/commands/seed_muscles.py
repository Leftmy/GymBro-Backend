from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.exercises.models import MuscleGroup

MUSCLE_GROUPS = [
    {
        "name": "Chest",
        "svg_id": "chest",
    },
    {
        "name": "Back",
        "svg_id": "back",
    },
    {
        "name": "Shoulders",
        "svg_id": "shoulders",
    },
    {
        "name": "Biceps",
        "svg_id": "biceps",
    },
    {
        "name": "Triceps",
        "svg_id": "triceps",
    },
    {
        "name": "Quadriceps",
        "svg_id": "quadriceps",
    },
    {
        "name": "Hamstrings",
        "svg_id": "hamstrings",
    },
    {
        "name": "Glutes",
        "svg_id": "glutes",
    },
    {
        "name": "Calves",
        "svg_id": "calves",
    },
    {
        "name": "Abs",
        "svg_id": "abs",
    },
]

class Command(BaseCommand):
    help = "Seed muscle groups"

    def handle(self, *args, **kwargs):
        created_count = 0

        for item in MUSCLE_GROUPS:
            obj, created = MuscleGroup.objects.get_or_create(
                name=item["name"],
                defaults={
                    "slug": slugify(item["name"]),
                    "svg_id": item["svg_id"],
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created muscle group: {obj.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Already exists: {obj.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_count} muscle groups."
            )
        )