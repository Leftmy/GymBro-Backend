from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.users.managers import UserManager

class UserRole(models.TextChoices):
    CLIENT = 'client', 'Client'
    TRAINER = 'trainer', 'Trainer'
    ADMIN = 'admin', 'Admin'

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_staff = models.BooleanField(
        default=False,
        help_text="Визначає, чи може користувач входити в адмін-панель."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Визначає, чи вважати користувача активним. Замість видалення акаунтів — деактивуйте їх."
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.CheckConstraint(
                check=models.Q(role__in=UserRole.values),
                name="check_valid_user_role",
            )
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"