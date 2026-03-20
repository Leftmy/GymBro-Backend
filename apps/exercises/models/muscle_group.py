from django.db import models
from common.core.models import BaseModel

class MuscleGroup(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    svg_id = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "muscle_groups"
        ordering = ["name"]
    
    def __str__(self):
        return self.name