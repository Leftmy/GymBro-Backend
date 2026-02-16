from django.db import models

class ExerciseMuscleGroup(models.Model):
    exercise = models.ForeignKey(
        'exercises.Exercise', 
        on_delete=models.CASCADE, 
        related_name='muscle_groups',
        db_index=True,
    )
    muscle_group = models.ForeignKey(
        'exercises.MuscleGroup', 
        on_delete=models.CASCADE, 
        related_name='exercise_muscle_groups',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    class Meta:
        db_table = 'exercise_muscle_groups'
        verbose_name = 'Exercise Muscle Group'
        verbose_name_plural = 'Exercise Muscle Groups'
        unique_together = ('exercise', 'muscle_group')

    def __str__(self):
        return f"{self.exercise.name} - {self.muscle_group.name}"