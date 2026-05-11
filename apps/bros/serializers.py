from rest_framework import serializers

from apps.bros.models import Bro
from apps.users.serializers import UserSerializer


class BroCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class BroUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["accepted"]
    )


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