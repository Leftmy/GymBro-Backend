from apps.workouts.models import WorkoutPlan
from django.db.models import Q
from apps.workouts.models import WorkoutPlan

def get_system_workouts():
    return WorkoutPlan.objects.filter(created_by_id=3)


def get_available_workouts(user):
    return WorkoutPlan.objects.filter(
        Q(created_by__role="admin") |
        Q(created_by=user)
    )