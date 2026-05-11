from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.bros.models import Bro

User = get_user_model()


class BroService:

    @staticmethod
    def send_bro_request(sender_id: int, receiver_id: int):
        if sender_id == receiver_id:
            raise ValueError("You cannot add yourself")

        if not User.objects.filter(id=receiver_id).exists():
            raise ValueError("User does not exist")

        existing_bro = Bro.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver_id)
            |
            Q(sender_id=receiver_id, receiver_id=sender_id)
        ).exists()

        if existing_bro:
            raise ValueError("Bro relationship already exists")

        bro = Bro.objects.create(
            sender_id=sender_id,
            receiver_id=receiver_id,
        )

        return bro

    @staticmethod
    def accept_bro_request(
        bro_id: int,
        user_id: int,
    ):
        bro = Bro.objects.filter(
            id=bro_id,
            receiver_id=user_id,
            status=Bro.Status.PENDING,
        ).first()

        if not bro:
            raise ValueError("Bro request not found")

        bro.status = Bro.Status.ACCEPTED
        bro.save(update_fields=["status"])

        return bro

    @staticmethod
    def remove_bro(
        user_id: int,
        bro_user_id: int,
    ):
        deleted_count, _ = Bro.objects.filter(
            (
                Q(sender_id=user_id, receiver_id=bro_user_id)
                |
                Q(sender_id=bro_user_id, receiver_id=user_id)
            ),
            status=Bro.Status.ACCEPTED,
        ).delete()

        return deleted_count > 0

    @staticmethod
    def get_bros(user_id: int):
        return Bro.objects.filter(
            (
                Q(sender_id=user_id)
                |
                Q(receiver_id=user_id)
            ),
            status=Bro.Status.ACCEPTED,
        ).select_related(
            "sender",
            "receiver",
        )

    @staticmethod
    def get_incoming_requests(user_id: int):
        return Bro.objects.filter(
            receiver_id=user_id,
            status=Bro.Status.PENDING,
        ).select_related("sender")

    @staticmethod
    def get_outgoing_requests(user_id: int):
        return Bro.objects.filter(
            sender_id=user_id,
            status=Bro.Status.PENDING,
        ).select_related("receiver")