# apps/bros/management/commands/seed_bros.py

import random

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.bros.models import Bro
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed bros relations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of bro relations to create"
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        count = kwargs["count"]

        users = list(User.objects.all())

        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR(
                    "Need at least 2 users"
                )
            )
            return

        statuses = [
            Bro.Status.PENDING,
            Bro.Status.ACCEPTED,
            Bro.Status.DECLINED,
        ]

        bros_to_create = []
        used_pairs = set()

        max_attempts = count * 10
        attempts = 0

        while len(bros_to_create) < count and attempts < max_attempts:
            sender = random.choice(users)
            receiver = random.choice(users)

            attempts += 1

            # prevent self relation
            if sender.id == receiver.id:
                continue

            pair = (sender.id, receiver.id)

            # prevent duplicates inside current seed
            if pair in used_pairs:
                continue

            # prevent duplicates in DB
            if Bro.objects.filter(
                sender=sender,
                receiver=receiver
            ).exists():
                continue

            used_pairs.add(pair)

            bros_to_create.append(
                Bro(
                    sender=sender,
                    receiver=receiver,
                    status=random.choice(statuses),
                )
            )

        created_bros = Bro.objects.bulk_create(
            bros_to_create,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(created_bros)} bro relations"
            )
        )

        if len(created_bros) < count:
            self.stdout.write(
                self.style.WARNING(
                    "Could not generate requested amount "
                    "because of unique constraints."
                )
            )