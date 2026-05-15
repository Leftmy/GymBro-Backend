# blog/api/post_api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import OpenApiParameter, extend_schema

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


class PostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
    summary="Get posts or single post",
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
    def get(self, request, post_id=None):

        # single post
        if post_id:
            post = get_post_by_id(post_id)

            if not post:
                return Response(
                    {"detail": "Not found"},
                    status=404,
                )

            return Response(PostSerializer(post).data)

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

        posts = list_posts(
            status=status_param,
            limit=limit,
            offset=offset,
        )

        return Response(
            PostSerializer(posts, many=True).data
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
        )

        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
    
class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update post",
        request=PostCreateUpdateSerializer,
        responses=PostSerializer,
    )
    def patch(self, request, post_id):
        post = get_post_by_id(post_id)

        if not post:
            return Response({"detail": "Not found"}, status=404)

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

        delete_post(post)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
