from django.db import models
from common.core.models import BaseModel
from .workout_plan import WorkoutPlan

class WorkoutPlanExercise(BaseModel):
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name="plan_exercises"
    )
    exercise = models.ForeignKey(
        "exercises.Exercise",
        on_delete=models.CASCADE,
        related_name="plan_links"
    )
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    rest_seconds = models.PositiveIntegerField(default=60)
    order = models.PositiveIntegerField(db_index=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_plan", "order"],
                name="unique_order_per_plan"
            )
        ]

    def __str__(self):
        return f"PlanExercise({self.workout_plan_id}, {self.exercise_id})"