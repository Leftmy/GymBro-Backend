from django.db import models
from common.core.models import BaseModel

class ExerciseMuscle(BaseModel):
    exercise = models.ForeignKey(
        "exercises.Exercise",
        on_delete=models.CASCADE,
        related_name="muscle_links"
    )

    muscle = models.ForeignKey(
        "exercises.MuscleGroup",
        on_delete=models.CASCADE,
        related_name="exercise_links"
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["exercise", "muscle"], name="unique_exercise_muscle")
        ]

    def __str__(self):
        return f"ExerciseMuscle({self.exercise_id}, {self.muscle_id})"