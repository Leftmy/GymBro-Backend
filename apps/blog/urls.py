# blog/urls.py

from django.urls import path

from apps.blog.views.comment_views import (
    CommentCreateAPIView,
    CommentDeleteAPIView,
    CommentListByPostAPIView,
)
from apps.blog.views.post_views import (
    PostAPIView,
    PostDetailAPIView,
)

urlpatterns = [
    # POSTS
    path("posts/", PostAPIView.as_view(), name="post-list-create"),
    path("posts/<uuid:post_id>/", PostDetailAPIView.as_view(), name="post-detail"),

    # COMMENTS
    path(
        "posts/<uuid:post_id>/comments/",
        CommentListByPostAPIView.as_view(),
        name="post-comments",
    ),

    path(
        "comments/",
        CommentCreateAPIView.as_view(),
        name="comment-create",
    ),

    path(
        "comments/<int:comment_id>/",
        CommentDeleteAPIView.as_view(),
        name="comment-delete",
    ),
]