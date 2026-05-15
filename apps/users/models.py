# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from common.core.models import BaseModel

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField


class UserRole(models.TextChoices):
    CLIENT = "client", "Client"
    TRAINER = "trainer", "Trainer"
    ADMIN = "admin", "Admin"


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        db_index=True,
    )

    username_normalized = models.CharField(
        max_length=150,
        editable=False,
        db_index=True,
    )

    class Meta:
        db_table = "users"

        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username_normalized"]),

            GinIndex(
                fields=["username_normalized"],
                name="user_username_norm_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def save(self, *args, **kwargs):
        self.username_normalized = self.username.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"