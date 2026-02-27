from django.shortcuts import render
from django.views import View
from apps.workouts.services import get_system_workouts

# Create your views here.
class WorkoutsView(View):
    def get(self, request):
        return render(request, "workouts.html")
    
class BuildAPlanView(View):
    def get(self, request):
        workouts = get_system_workouts()
        return render(request, "general/buildaplan.html", {
            "workouts": workouts
        })