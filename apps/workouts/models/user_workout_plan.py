from django.db import models
from django.conf import settings
from common.core.models import BaseModel
from .workout_plan import WorkoutPlan

User = settings.AUTH_USER_MODEL
class UserWorkoutPlan(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_plans")
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    started_at = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_active=True),
                name="unique_active_plan_per_user"
            ),
            models.UniqueConstraint(fields=["user", "workout_plan"], name="unique_user_plan")
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.user.username} - {self.workout_plan.name} [{status}]"