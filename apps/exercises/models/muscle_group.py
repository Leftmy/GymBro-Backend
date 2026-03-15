from django.db import models

class MuscleGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    svg_id = models.CharField(
        max_length=100, 
        unique=True, 
        # help_text="ID елемента в SVG-карті тіла (наприклад, 'muscle-biceps')"
    )
    
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'muscle_groups'
        verbose_name = 'Muscle Group'
        verbose_name_plural = 'Muscle Groups'
        ordering = ['name']

    def __str__(self):
        return self.name