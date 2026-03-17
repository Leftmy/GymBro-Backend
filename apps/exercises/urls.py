from django.urls import path
from apps.exercises.views import ExercisesAPIView, ExerciseDetailAPIView

urlpatterns = [
    path("exercises/", ExercisesAPIView.as_view(), name="exercises"),
    path('exercises/<int:pk>/', ExerciseDetailAPIView.as_view()),
]