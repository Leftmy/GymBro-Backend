from django.urls import path


from .views import WorkoutsView, BuildAPlanView
urlpatterns = [
    path('workouts/', WorkoutsView.as_view(), name="workouts"),
    path('buildaplan/', BuildAPlanView.as_view(), name='buildaplan'),
]