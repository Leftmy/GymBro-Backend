from django.shortcuts import render
from django.views import View
from services import get_system_workouts

# Create your views here.
class WorkoutsView(View):
    def get(self, request):
        workouts = get_system_workouts() if not None else None
        print("WORKOUTS COUNT:", workouts.count())
        data = {"workouts" : workouts}
        return render(request, "workouts.html", context=data)
    
class BuildAPlanView(View):
    def get(self, request):
        return render(request, "general/buildaplan.html")