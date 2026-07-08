from django.urls import path

from apps.bros.views import BroAPIView, BroDetailAPIView

urlpatterns = [
    path("", BroAPIView.as_view(), name="handle-bros"),
    path("<int:bro_id>/", BroDetailAPIView.as_view(), name="bro-details"),
]
