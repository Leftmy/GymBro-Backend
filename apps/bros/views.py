from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.bros.constants import BroListType
from apps.bros.services.commands import BroCommands
from apps.bros.services.queries import BroQueries
from apps.bros.serializers import (
    BroSerializer,
    BroCreateSerializer,
    BroUpdateSerializer,
)


class BroAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                enum=BroListType.CHOICES,
            ),
        ],
        responses=BroSerializer(many=True),
    )
    def get(self, request):
        bro_type = request.query_params.get(
            "type",
            BroListType.ACCEPTED,
        )

        bros = BroQueries.get_bros(
            user_id=request.user.id,
            bro_type=bro_type,
        )

        return Response(
            BroSerializer(bros, many=True).data
        )

    @extend_schema(
        request=BroCreateSerializer,
        responses={201: BroSerializer},
    )
    def post(self, request):
        serializer = BroCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bro = BroCommands.send_bro_request(
            sender_id=request.user.id,
            receiver_id=serializer.validated_data["user_id"],
        )

        return Response(
            BroSerializer(bro).data,
            status=status.HTTP_201_CREATED,
        )


class BroDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BroUpdateSerializer,
        responses={200: BroSerializer},
    )
    def patch(self, request, bro_id):
        serializer = BroUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bro = BroCommands.update_bro_status(
            bro_id=bro_id,
            user_id=request.user.id,
            status=serializer.validated_data["status"],
        )

        return Response(BroSerializer(bro).data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="bro_id",
                type=int,
            ),
        ],
        responses={204: None},
    )
    def delete(self, request, bro_id):
        deleted = BroCommands.delete_bro(
            bro_id=bro_id,
            user_id=request.user.id,
        )

        if not deleted:
            return Response(
                {"detail": "Bro not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)