# blog/services/post_service.py

from django.utils import timezone
from django.db.models import Q
from apps.blog.models import Post, PostStatus


def create_post(*, title: str, body: str, author=None, labels=None) -> Post:
    return Post.objects.create(
        title=title,
        body=body,
        author=author,
        labels=labels or []
    )


ALLOWED_UPDATE_FIELDS = {"title", "body", "labels"}

def update_post(post: Post, **kwargs) -> Post:
    for field, value in kwargs.items():
        if field in ALLOWED_UPDATE_FIELDS:
            setattr(post, field, value)

    post.save(update_fields=list(kwargs.keys()))
    return post


def delete_post(post: Post) -> None:
    post.delete()


def publish_post(post: Post) -> Post:
    post.status = PostStatus.PUBLISHED
    post.published_at = timezone.now()
    post.save(update_fields=["status", "published_at"])
    return post


def archive_post(post: Post) -> Post:
    post.status = PostStatus.ARCHIVED
    post.save(update_fields=["status"])
    return post


def get_post_by_id(post_id) -> Post:
    try:
        return Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None


def get_post_with_comments(post_id):
    return Post.objects.prefetch_related("comments").filter(id=post_id).first()


def list_posts(*, status=None, author=None):
    qs = Post.objects.select_related("author")

    if status:
        qs = qs.filter(status=status)

    if author:
        qs = qs.filter(author=author)

    return qs



def search_posts(query: str):
    return Post.objects.filter(
        Q(title__icontains=query) |
        Q(body__icontains=query)
    )