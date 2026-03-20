from django.urls import path
from apps.exercises.views import MusclesView, ExerciseView

urlpatterns = [
    path("muscles/", MusclesView.as_view(), name="muscles"),
    path('exercises/', ExerciseView.as_view()),
]