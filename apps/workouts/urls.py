from django.urls import path
from apps.workouts.views import WorkoutsView, WorkoutsDetailView

urlpatterns = [
    path("workouts/", WorkoutsView.as_view(), name="workout-list"),
    path("workouts/<int:pk>/", WorkoutsDetailView.as_view(), name="workout-detail"),
]