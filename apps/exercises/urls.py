from django.urls import path
from apps.exercises.views import MusclesView

urlpatterns = [
    path("muscles/", MusclesView.as_view(), name="muscles"),
    # path('exercises/<int:pk>/', ExerciseDetailAPIView.as_view()),
]