# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from common.core.models import BaseModel

class UserRole(models.TextChoices):
    CLIENT = "client", "Client"
    TRAINER = "trainer", "Trainer"
    ADMIN = "admin", "Admin"

class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username']
    
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        db_index=True,
    )

    class Meta:
        db_table = "users"
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"