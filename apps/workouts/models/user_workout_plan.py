from django.db import models
from django.conf import settings
from common.core.models import BaseModel
from .workout_plan import WorkoutPlan

User = settings.AUTH_USER_MODEL
class DayOfWeek(models.IntegerChoices):
    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
    SATURDAY = 6, "Saturday"
    SUNDAY = 7, "Sunday"


class UserWorkoutPlan(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_plans")
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    started_at = models.DateField(null=True, blank=True)

    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices,
        null=True,
        blank=True,
        db_index=True
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_active=True),
                name="unique_active_plan_per_user"
            ),
            models.UniqueConstraint(
                fields=["user", "day_of_week"],
                name="unique_day_per_user"
            ),
            models.UniqueConstraint(fields=["user", "workout_plan"], name="unique_user_plan")
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.user.username} - {self.workout_plan.name} [{status}]"