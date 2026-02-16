from django.db import models

# Create your models here.
class WorkoutPlan(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_workout_plans', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'workout_plans'
        verbose_name = 'Workout Plan'
        verbose_name_plural = 'Workout Plans'
        unique_together = ('name', 'created_by')

    def __str__(self):
        return self.name