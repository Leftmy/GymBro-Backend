from django.urls import path
from .views import PlansAPIView, PlansDetailsAPIView

urlpatterns = [
    path('v1/plans/', PlansAPIView.as_view(), name='workout-plans'),
    path('v1/plans/<int:pk>/', PlansDetailsAPIView.as_view(), name='workout-plan-detail'),
]