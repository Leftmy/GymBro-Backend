# blog/api/post_api.py

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.blog.models import PostStatus
from apps.blog.serializers.post_serializer import (
    PostCreateUpdateSerializer,
    PostSerializer,
)
from apps.blog.services.post_service import (
    create_post,
    delete_post,
    get_post_by_id,
    list_posts,
    update_post,
)


class PostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get posts",
        parameters=[
            OpenApiParameter(
                name="status",
                type=str,
                required=False,
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                required=False,
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                required=False,
            ),
        ],
        responses=PostSerializer(many=True),
    )
    def get(self, request):
        # query params
        status_param = request.query_params.get("status")

        try:
            limit = int(request.query_params.get("limit", 20))
        except ValueError:
            limit = 20

        try:
            offset = int(request.query_params.get("offset", 0))
        except ValueError:
            offset = 0

        queryset = list_posts(status=status_param, viewer=request.user)

        total = queryset.count()
        posts = queryset[offset : offset + limit]

        serializer = PostSerializer(posts, many=True)

        return Response(
            {
                "total": total,
                "results": serializer.data,
            }
        )

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
            status=serializer.validated_data.get("status"),
        )

        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get single post",
        responses=PostSerializer,
    )
    def get(self, request, post_id):
        post = get_post_by_id(post_id)

        if not post:
            return Response(
                {"detail": "Not found"},
                status=404,
            )

        return Response(PostSerializer(post).data)

    @extend_schema(
        summary="Update post",
        request=PostCreateUpdateSerializer,
        responses=PostSerializer,
    )
    def patch(self, request, post_id):
        post = get_post_by_id(post_id)

        if not post:
            return Response({"detail": "Not found"}, status=404)

        # Only the author can update the post and only while it's a draft
        if post.author != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if post.status != PostStatus.DRAFT:
            return Response(
                {"detail": "Cannot edit published post"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PostCreateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        post = update_post(post, **serializer.validated_data)

        return Response(PostSerializer(post).data)

    @extend_schema(
        summary="Delete post",
        responses={204: None},
    )
    def delete(self, request, post_id):
        post = get_post_by_id(post_id)

        if not post:
            return Response({"detail": "Not found"}, status=404)

        # Only the author can delete the post and only while it's a draft
        if post.author != request.user:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        if post.status != PostStatus.DRAFT:
            return Response(
                {"detail": "Cannot delete published post"},
                status=status.HTTP_403_FORBIDDEN,
            )

        delete_post(post)

        return Response(status=status.HTTP_204_NO_CONTENT)
