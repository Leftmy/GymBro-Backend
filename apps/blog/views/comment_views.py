# blog/api/post_api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema

from apps.blog.serializers.comment_serializer import CommentCreateSerializer, CommentSerializer
from apps.blog.services.comment_service import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_comments_for_post,
)

from apps.blog.services.post_service import get_post_by_id
from common.core.base_cursor_pagination import BaseCursorPagination



class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create comment",
        request=CommentCreateSerializer,
        responses={
            201: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"}
                    }
                }
            )
        }
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
    
class CommentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Delete comment",
        responses={204: None},
    )
    def delete(self, request, comment_id):
        comment = get_comment_by_id(comment_id)

        if not comment:
            return Response({"detail": "Not found"}, status=404)

        if comment.user != request.user:
            return Response(
                {"detail": "Forbidden"},
                status=status.HTTP_403_FORBIDDEN
            )

        delete_comment(comment)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CommentListByPostAPIView(APIView):
    @extend_schema(
        summary="Get comments for post",
        responses=CommentSerializer(many=True),
    )
    def get(self, request, post_id):
        post = get_post_by_id(post_id)

        if not post:
            return Response({"detail": "Not found"}, status=404)

        comments = get_comments_for_post(post=post)

        paginator = BaseCursorPagination()
        page = paginator.paginate_queryset(comments, request)

        serializer = CommentSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)