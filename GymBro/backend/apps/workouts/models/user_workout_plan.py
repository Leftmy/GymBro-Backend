from django.db import models

# Create your models here.
class UserWorkoutPlan(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_workout_plans', db_index=True)
    workout_plan = models.ForeignKey('workouts.WorkoutPlan', on_delete=models.CASCADE, related_name='user_workout_plans', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'user_workout_plans'
        verbose_name = 'User Workout Plan'
        verbose_name_plural = 'User Workout Plans'
        unique_together = ('user_id', 'workout_plan')

    def __str__(self):
        return f"User {self.user_id} - {self.workout_plan.name}"