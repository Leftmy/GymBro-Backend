# apps/exercises/models.py
from django.db import IntegrityError, models
from django.utils.text import slugify
import uuid

from django.db import transaction
from common.core.models import BaseModel

class Exercise(BaseModel):
    class Difficulty(models.IntegerChoices):
        BEGINNER = 1, "Beginner"
        INTERMEDIATE = 2, "Intermediate"
        ADVANCED = 3, "Advanced"

    class Equipment(models.TextChoices):
        BARBELL = "barbell", "Barbell"
        DUMBBELL = "dumbbell", "Dumbbell"
        MACHINE = "machine", "Machine"
        BODYWEIGHT = "bodyweight", "Bodyweight"

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    difficulty = models.IntegerField(choices=Difficulty.choices, default=Difficulty.BEGINNER)
    equipment = models.CharField(max_length=20, choices=Equipment.choices, blank=True)

    muscles = models.ManyToManyField(
        "MuscleGroup",
        through="ExerciseMuscle",
        related_name="exercises"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug

            for _ in range(5):  # retry
                try:
                    with transaction.atomic():
                        self.slug = slug
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        else:
            super().save(*args, **kwargs)

    class Meta:
        db_table = "exercises"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["difficulty"]),
            models.Index(fields=["equipment"]),
        ]

    def __str__(self):
        return self.name