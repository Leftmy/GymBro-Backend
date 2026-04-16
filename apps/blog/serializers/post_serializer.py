# blog/serializers/post_serializer.py

from rest_framework import serializers
from apps.blog.models import Post
from apps.blog.serializers.comment_serializer import CommentSerializer

class PostSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "author",
            "status",
            "labels",
            "created_at",
            "updated_at",
            "published_at",
            "comments_count",
        ]

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "body", "labels"]