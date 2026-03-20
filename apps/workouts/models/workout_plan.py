from django.db import models
from django.conf import settings
from common.core.models import BaseModel

User = settings.AUTH_USER_MODEL

class WorkoutPlan(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_plans",
        db_index=True
    )
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = "workout_plans"
        constraints = [
            models.UniqueConstraint(
            fields=["name", "created_by"],
            name="unique_plan_per_user"
            )
        ]

    def __str__(self):
        return self.name