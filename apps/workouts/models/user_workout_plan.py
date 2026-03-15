from django.db import models
from django.conf import settings

class UserWorkoutPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='plan_assignments',
        db_index=True
    )
    workout_plan = models.ForeignKey(
        'workouts.WorkoutPlan', 
        on_delete=models.CASCADE, 
        related_name='assigned_users',
        db_index=True
    )
    
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_workout_plans'
        verbose_name = 'User Workout Plan'
        verbose_name_plural = 'User Workout Plans'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'workout_plan'], 
                name='unique_user_plan_assignment'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.workout_plan.name}"