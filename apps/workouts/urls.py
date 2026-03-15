from django.urls import path
from .views import PlansAPIView, PlansDetailsAPIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('v1/plans/', PlansAPIView.as_view(), name='workout-plans'),
    path('v1/plans/<int:pk>/', PlansDetailsAPIView.as_view(), name='workout-plan-detail'),
]