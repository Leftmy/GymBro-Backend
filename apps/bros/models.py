from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Bro(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_bros",
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_bros",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bros"

        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"],
                name="unique_bro_relation",
            ),

            models.CheckConstraint(
                condition=~models.Q(
                    sender=models.F("receiver")
                ),
                name="prevent_self_bro",
            ),
        ]

        indexes = [
            models.Index(fields=["sender", "status"]),
            models.Index(fields=["receiver", "status"]),
        ]

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"