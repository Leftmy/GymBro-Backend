# blog/serializers/post_serializer.py

from rest_framework import serializers
from apps.blog.models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "user", "body", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
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
            "comments",
        ]

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "body", "labels"]