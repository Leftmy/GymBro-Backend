from django.urls import path
from .views import WorkoutsView, BuildAPlanView, get_exercises_by_muscle

urlpatterns = [
    path('workouts/', WorkoutsView.as_view(), name="workouts"),
    path('buildaplan/', BuildAPlanView.as_view(), name='buildaplan'),
    path('api/exercises/', get_exercises_by_muscle, name='ajax-exercises')

]