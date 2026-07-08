# blog/serializers/post_serializer.py

from rest_framework import serializers

from apps.blog.models import Post, PostStatus


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
    status = serializers.ChoiceField(choices=PostStatus.choices, required=False)

    class Meta:
        model = Post
        fields = ["title", "body", "labels", "status"]
