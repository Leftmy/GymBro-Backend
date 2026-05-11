from rest_framework import serializers

from apps.bros.models import Bro
from apps.users.serializers import UserSerializer


class BroCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class BroActionSerializer(serializers.Serializer):
    bro_id = serializers.IntegerField()


class BroSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Bro
        fields = [
            "id",
            "sender",
            "receiver",
            "status",
            "created_at",
        ]