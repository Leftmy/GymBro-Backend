from django.shortcuts import render

# blog/api/post_api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from apps.blog.services.post_service import (
    create_post,
    get_post_by_id,
    list_posts,
    update_post,
    delete_post,
)

from apps.blog.serializers.post_serializer import (
    PostSerializer,
    PostCreateUpdateSerializer,
)

from apps.blog.services.comment_service import create_comment, delete_comment, get_comment_by_id
from apps.blog.serializers.comment_serializer import CommentCreateSerializer

class PostAPIView(APIView):

    @extend_schema(
        summary="Get list of posts",
        description="Retrieve all posts or filter by status",
        responses=PostSerializer(many=True),
    )
    def get(self, request, post_id=None):
        if post_id:
            post = get_post_by_id(post_id)
            if not post:
                return Response({"detail": "Not found"}, status=404)

            return Response(PostSerializer(post).data)

        status_param = request.query_params.get("status")
        posts = list_posts(status=status_param)

        return Response(PostSerializer(posts, many=True).data)
    
    @extend_schema(
        summary="Create post",
        request=PostCreateUpdateSerializer,
        responses=PostSerializer,
    )
    def post(self, request):
        serializer = PostCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = create_post(
            title=serializer.validated_data["title"],
            body=serializer.validated_data["body"],
            author=request.user,
            labels=serializer.validated_data.get("labels"),
        )

        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
    

    @extend_schema(
    summary="Partially update post",
    request=PostCreateUpdateSerializer,
    responses=PostSerializer,
    )
    def patch(self, request, post_id):
        post = get_post_by_id(post_id)

        if not post:
            return Response({"detail": "Not found"}, status=404)

        serializer = PostCreateUpdateSerializer(
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        post = update_post(post, **serializer.validated_data)

        return Response(PostSerializer(post).data)
    
    @extend_schema(
        summary="Delete post",
        description="Delete post by ID",
    )
    def delete(self, request, post_id):
        post = get_post_by_id(post_id)

        if not post:
            return Response({"detail": "Not found"}, status=404)

        delete_post(post)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CommentAPIView(APIView):

    @extend_schema(
        summary="Create comment",
        request=CommentCreateSerializer,
    )
    def post(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = create_comment(
            post=serializer.validated_data["post"],
            user=request.user,
            body=serializer.validated_data["body"],
        )

        return Response({"id": comment.id}, status=201)
    
    @extend_schema(
        summary="Delete comment",
        description="Delete comment by ID",
        responses={204: None},
    )
    def delete(self, request, comment_id):
        comment = get_comment_by_id(comment_id)

        if not comment:
            return Response({"detail": "Not found"}, status=404)

        if comment.user != request.user:
            return Response(
                {"detail": "You cannot delete this comment"},
                status=status.HTTP_403_FORBIDDEN
            )

        delete_comment(comment)

        return Response(status=status.HTTP_204_NO_CONTENT)