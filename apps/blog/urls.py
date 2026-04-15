# blog/urls.py

from django.urls import path
from apps.blog.views import PostAPIView, CommentAPIView

urlpatterns = [
    path("posts/", PostAPIView.as_view()),
    path("comments/", CommentAPIView.as_view()),
]