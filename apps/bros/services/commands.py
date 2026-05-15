from uuid import UUID

from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.bros.models import Bro

User = get_user_model()


class BroCommands:

    @staticmethod
    def send_bro_request(
        sender_id: int,
        receiver_uuid: UUID,
    ):

        receiver = (
            User.objects
            .only("id")
            .filter(uuid=receiver_uuid)
            .first()
        )

        if not receiver:
            raise ValueError("User does not exist")

        if sender_id == receiver.id:
            raise ValueError("You cannot add yourself")

        exists = Bro.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver.id)
            |
            Q(sender_id=receiver.id, receiver_id=sender_id)
        ).exists()

        if exists:
            raise ValueError("Bro relation already exists")

        return Bro.objects.create(
            sender_id=sender_id,
            receiver_id=receiver.id,
        )

    @staticmethod
    def update_bro_status(
        bro_id: int,
        user_id: int,
        status: str,
    ):

        bro = Bro.objects.filter(
            id=bro_id,
            receiver_id=user_id,
        ).first()

        if not bro:
            raise ValueError("Bro request not found")

        if bro.status != Bro.Status.PENDING:
            raise ValueError("Bro request already processed")

        if status not in Bro.Status.values:
            raise ValueError("Invalid status")

        bro.status = status
        bro.save(update_fields=["status"])

        return bro
    
    @staticmethod
    def delete_bro(bro_id: int, user_id: int):
        deleted_count, _ = Bro.objects.filter(
            id=bro_id
        ).filter(
            Q(sender_id=user_id) | Q(receiver_id=user_id)
        ).delete()

        return deleted_count > 0