from uuid import UUID

from django.db.models import Q
from apps.bros.models import Bro
from apps.bros.constants import BroListType


class BroQueries:

    @staticmethod
    def get_bros(user_id: int, bro_type: str):
        if bro_type not in BroListType.CHOICES:
            raise ValueError("Invalid bro type")

        if bro_type == BroListType.ACCEPTED:
            return Bro.objects.filter(
                Q(sender_id=user_id) | Q(receiver_id=user_id),
                status=Bro.Status.ACCEPTED,
            ).select_related("sender", "receiver")

        if bro_type == BroListType.INCOMING:
            return Bro.objects.filter(
                receiver_id=user_id,
                status=Bro.Status.PENDING,
            ).select_related("sender")

        if bro_type == BroListType.OUTGOING:
            return Bro.objects.filter(
                sender_id=user_id,
                status=Bro.Status.PENDING,
            ).select_related("receiver")

        return Bro.objects.none()