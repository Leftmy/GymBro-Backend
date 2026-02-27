from apps.workouts.models import WorkoutPlan
from django.db.utils import IntegrityError

def get_system_workouts():
    return WorkoutPlan.objects.filter(created_by_id=3)