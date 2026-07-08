from django.contrib import admin

from .models import Bro


@admin.register(Bro)
class BroAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("sender__username", "receiver__username")
    raw_id_fields = ("sender", "receiver")
