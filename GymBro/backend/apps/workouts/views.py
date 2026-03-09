from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.workouts.services import get_available_workouts
from apps.exercises.services import get_all_exercises_by_muscle_group

# Create your views here.
class WorkoutsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "workouts.html")
    
class BuildAPlanView(View):
    def get(self, request):

        workouts = get_available_workouts(request.user)
        exercises = get_all_exercises_by_muscle_group("Back")

        return render(request, "general/buildaplan.html", {
            "workouts": workouts,
            "exercises": exercises
        })
    
def get_exercises_by_muscle(request):
    muscle = request.GET.get('muscle')
    exercises = get_all_exercises_by_muscle_group(muscle)
    data = [
        {"id": ex.id, "name": ex.name}
        for ex in exercises
    ]

    return JsonResponse({"exercises": data})
