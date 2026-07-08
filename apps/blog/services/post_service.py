# blog/services/post_service.py

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone

from apps.blog.models import Post, PostStatus


def create_post(
    *, title: str, body: str, author=None, labels=None, status=None
) -> Post:
    published_at = None
    if status == PostStatus.PUBLISHED:
        published_at = timezone.now()

    return Post.objects.create(
        title=title,
        body=body,
        author=author,
        labels=labels or [],
        status=status or PostStatus.DRAFT,
        published_at=published_at,
    )


ALLOWED_UPDATE_FIELDS = {"title", "body", "labels", "status"}


def update_post(post: Post, **kwargs) -> Post:
    # Update allowed fields
    for field, value in kwargs.items():
        if field in ALLOWED_UPDATE_FIELDS:
            setattr(post, field, value)

    # Handle published_at when status changes
    update_fields = set(k for k in kwargs.keys() if k in ALLOWED_UPDATE_FIELDS)
    if "status" in kwargs:
        if kwargs.get("status") == PostStatus.PUBLISHED:
            post.published_at = timezone.now()
            update_fields.add("published_at")
        else:
            post.published_at = None
            update_fields.add("published_at")

    post.save(update_fields=list(update_fields))
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


def list_posts(
    *,
    status=None,
    author=None,
    viewer=None,
):
    """
    Return posts filtered by status/author.

    - If `status` is None, default to published posts. If `viewer` is provided,
      include the viewer's drafts as well (they will be ordered above published posts).
    - If `status` is provided, filter strictly by that status (e.g. 'archived').
    """
    qs = Post.objects.select_related("author")

    # Default behavior: only published posts,
    # but include viewer's drafts when applicable
    if status is None:
        if viewer:
            qs = qs.filter(
                Q(status=PostStatus.PUBLISHED)
                | (Q(status=PostStatus.DRAFT) & Q(author=viewer))
            )
        else:
            qs = qs.filter(status=PostStatus.PUBLISHED)
    else:
        qs = qs.filter(status=status)

    if author:
        qs = qs.filter(author=author)

    # Annotate and order so that the viewer's drafts appear above others
    if viewer:
        qs = qs.annotate(
            _user_draft=Case(
                When(Q(author=viewer, status=PostStatus.DRAFT), then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("_user_draft", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    return qs


def search_posts(query: str):
    return Post.objects.filter(Q(title__icontains=query) | Q(body__icontains=query))
