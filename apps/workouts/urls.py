from django.urls import path
from apps.workouts.views import UserWorkoutPlanDetailView, UserWorkoutPlanView, WorkoutsView, WorkoutsDetailView

urlpatterns = [
    path("workouts/", WorkoutsView.as_view(), name="workout-list"),
    path("workouts/<int:pk>/", WorkoutsDetailView.as_view(), name="workout-detail"),
     path("user-workouts/", UserWorkoutPlanView.as_view()),
    path("user-workouts/<int:pk>/", UserWorkoutPlanDetailView.as_view()),
]