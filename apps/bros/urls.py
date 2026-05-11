from apps.bros.views import BroAPIView, BroDetailAPIView
from django.urls import path


urlpatterns = [
    path("", BroAPIView.as_view(), name="handle-bros"),
    path("<int:bro_id>/", BroDetailAPIView.as_view(), name="bro-details"),
]