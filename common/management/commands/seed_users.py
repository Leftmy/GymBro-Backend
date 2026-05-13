# apps/users/management/commands/seed_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker
import random

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed users data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of users to create"
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        count = kwargs["count"]

        roles = ["client", "trainer"]

        users_to_create = []

        for i in range(count):
            role = random.choice(roles)

            username = f"{fake.user_name()}{i}"
            email = f"{username}@example.com"

            users_to_create.append(
                User(
                    username=username,
                    email=email,
                    role=role,
                )
            )

        created_users = User.objects.bulk_create(users_to_create)

        # bulk_create не викликає save()
        for user in created_users:
            user.set_password("password123")
            user.save(update_fields=["password"])

        # Create admin
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123",
                role="admin",
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {count} users"
            )
        )