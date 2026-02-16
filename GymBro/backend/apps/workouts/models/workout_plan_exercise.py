from django.db import models

# Create your models here.
class WorkoutPlanExercise(models.Model):
    workout_plan = models.ForeignKey('workouts.WorkoutPlan', on_delete=models.CASCADE, related_name='exercises', db_index=True)
    exercise = models.ForeignKey('exercises.Exercise', on_delete=models.CASCADE, related_name='workout_plans', db_index=True)
    sets = models.IntegerField(null=False, blank=False)
    reps = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'workout_plan_exercises'
        verbose_name = 'Workout Plan Exercise'
        verbose_name_plural = 'Workout Plan Exercises'
        unique_together = ('workout_plan', 'exercise')

    def __str__(self):
        return f"{self.workout_plan.name} - {self.exercise.name}"