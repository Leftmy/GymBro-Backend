# apps/blog/management/commands/seed_blog.py

import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from faker import Faker

from apps.blog.models import Post, Comment, PostStatus
from apps.users.models import User


fake = Faker()


class Command(BaseCommand):
    help = "Seed blog posts and comments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--posts",
            type=int,
            default=30,
            help="Number of posts to create"
        )

        parser.add_argument(
            "--comments",
            type=int,
            default=100,
            help="Number of comments to create"
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        posts_count = kwargs["posts"]
        comments_count = kwargs["comments"]

        users = list(User.objects.all())

        if not users:
            self.stdout.write(
                self.style.ERROR(
                    "No users found. Seed users first."
                )
            )
            return

        statuses = [
            PostStatus.DRAFT,
            PostStatus.PUBLISHED,
            PostStatus.ARCHIVED,
        ]

        possible_labels = [
            "fitness",
            "health",
            "nutrition",
            "training",
            "cardio",
            "strength",
            "wellness",
            "recovery",
            "mindset",
            "sport",
        ]

        posts_to_create = []

        for _ in range(posts_count):
            status = random.choice(statuses)

            published_at = (
                timezone.now()
                if status == PostStatus.PUBLISHED
                else None
            )

            labels = random.sample(
                possible_labels,
                k=random.randint(1, 4)
            )

            posts_to_create.append(
                Post(
                    title=fake.sentence(nb_words=6),
                    body="\n\n".join(fake.paragraphs(nb=5)),
                    author=random.choice(users),
                    status=status,
                    labels=labels,
                    published_at=published_at,
                )
            )

        created_posts = Post.objects.bulk_create(posts_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(created_posts)} posts"
            )
        )

        comments_to_create = []

        for _ in range(comments_count):
            comments_to_create.append(
                Comment(
                    post=random.choice(created_posts),
                    user=random.choice(users),
                    body=fake.paragraph(nb_sentences=3),
                )
            )

        created_comments = Comment.objects.bulk_create(comments_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(created_comments)} comments"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Blog seed completed successfully"
            )
        )