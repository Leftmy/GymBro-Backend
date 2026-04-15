import uuid

from django.db import models


class PostStatus(models.TextChoices):
    DRAFT = "draft", "DRAFT"
    PUBLISHED = "published", "PUBLISHED"
    ARCHIVED = "archived", "ARCHIVED"


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)
    body = models.TextField()

    author = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts"
    )

    status = models.CharField(
        max_length=10,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT,
    )

    labels = models.JSONField(default=list, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]

class Comment(models.Model):
    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name="comments"
    )

    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment({self.user_id}, {self.post_id})"
    
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        indexes = [
            models.Index(fields=["post", "created_at"]),
        ]