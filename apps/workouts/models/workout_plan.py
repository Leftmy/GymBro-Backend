from django.db import models
from django.conf import settings

class WorkoutPlan(models.Model):
    name = models.CharField(max_length=100) 
    description = models.TextField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_workout_plans',
        db_index=True
    )

    exercises = models.ManyToManyField('exercises.Exercise', through='WorkoutPlanExercise', related_name='workout_plans')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_plans'
        verbose_name = 'Workout Plan'
        verbose_name_plural = 'Workout Plans'
        
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'created_by'], 
                name='unique_plan_name_per_user'
            )
        ]

    def __str__(self):
        owner = self.created_by.username if self.created_by else "Deleted User"
        return f"{self.name} (by {owner})"