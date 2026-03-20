# core/models.py
import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True