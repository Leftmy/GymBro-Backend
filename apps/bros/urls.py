from apps.bros.views import BroAPIView, AcceptBroAPIView, RemoveBroAPIView
from django.urls import path


urlpatterns = [
    path("", BroAPIView.as_view(), name="handle-bros"),
    path("accept/", AcceptBroAPIView.as_view(), name="accept-bro"),
    path("remove/", RemoveBroAPIView.as_view(), name="remove-bro")
]