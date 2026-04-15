# blog/serializers/comment_serializer.py

from rest_framework import serializers
from apps.blog.models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["post", "body"]