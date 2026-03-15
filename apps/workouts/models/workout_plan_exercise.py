from django.db import models

class WorkoutPlanExercise(models.Model):
    workout_plan = models.ForeignKey(
        'workouts.WorkoutPlan', 
        on_delete=models.CASCADE, 
        related_name='plan_exercises'
    )
    exercise = models.ForeignKey(
        'exercises.Exercise', 
        on_delete=models.CASCADE, 
        related_name='plan_appearances'
    )
    
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    rest_seconds = models.PositiveIntegerField(default=60)
    
    order = models.PositiveIntegerField(
        default=0, 
        help_text="Порядок вправи у тренуванні"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workout_plan_exercises'
        verbose_name = 'Workout Plan Exercise'
        verbose_name_plural = 'Workout Plan Exercises'
        ordering = ['order', 'created_at']
        
        constraints = [
            models.UniqueConstraint(
                fields=['workout_plan', 'order'], 
                name='unique_order_per_plan'
            )
        ]

    def __str__(self):
        return f"{self.workout_plan.name}: {self.exercise.name} (Step {self.order})"