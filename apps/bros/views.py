from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.bros.services import BroService
from apps.bros.serializers import (
    BroSerializer,
    BroCreateSerializer,
    BroActionSerializer,
)


class BroAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bros = BroService.get_bros(
            request.user.id
        )

        serializer = BroSerializer(
            bros,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = BroCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            bro = BroService.send_bro_request(
                sender_id=request.user.id,
                receiver_id=serializer.validated_data["user_id"],
            )

            return Response(
                BroSerializer(bro).data,
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AcceptBroAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BroActionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            bro = BroService.accept_bro_request(
                bro_id=serializer.validated_data["bro_id"],
                user_id=request.user.id,
            )

            return Response(
                BroSerializer(bro).data
            )

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RemoveBroAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = BroCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        deleted = BroService.remove_bro(
            user_id=request.user.id,
            bro_user_id=serializer.validated_data["user_id"],
        )

        if not deleted:
            return Response(
                {"detail": "Bro relation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )