from django.db import models

class Exercise(models.Model):
    class Difficulty(models.IntegerChoices):
        BEGINNER = 1, 'Beginner'
        INTERMEDIATE = 2, 'Intermediate'
        ADVANCED = 3, 'Advanced'
        PRO = 4, 'Pro'

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    
    difficulty_level = models.IntegerField(
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
        db_index=True
    )

    muscles = models.ManyToManyField('MuscleGroup', through='ExerciseMuscleGroup', related_name='exercises')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exercises'
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_difficulty_level_display()})"