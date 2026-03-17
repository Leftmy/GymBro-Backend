from django.db import models

class ExerciseMuscleGroup(models.Model):
    exercise = models.ForeignKey(
        'Exercise',
        on_delete=models.CASCADE, 
        related_name='exercise_muscles',
        db_index=True,
    )
    muscle_group = models.ForeignKey(
        'MuscleGroup', 
        on_delete=models.CASCADE, 
        related_name='muscle_exercises',
        db_index=True,
    )
    
    is_primary = models.BooleanField(
        default=False, 
        help_text="Чи є цей м'яз основним для даної вправи?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exercise_muscle_groups'
        verbose_name = 'Exercise Muscle Group'
        verbose_name_plural = 'Exercise Muscle Groups'
        constraints = [
            models.UniqueConstraint(
                fields=['exercise', 'muscle_group'], 
                name='unique_exercise_muscle'
            )
        ]

    def __str__(self):
        return f"{self.exercise.name} -> {self.muscle_group.name}"