from .models import WorkoutPlan

def get_all_workout_plans():
    return WorkoutPlan.objects.all()

def get_all_workout_plan_by_user(user_id: int):
    return WorkoutPlan.objects.filter(created_by_id=user_id)

def get_workout_plan_by_id(wkt_id: int):
    return WorkoutPlan.objects.get(id=wkt_id)

def create_workout_plan(name: str, created_by, description: str = None) -> WorkoutPlan:
    return WorkoutPlan.objects.create(
        name=name,
        description=description,
        created_by=created_by
    )

def update_workout_plan(workout_plan: WorkoutPlan, **data) -> WorkoutPlan:
    for field, value in data.items():
        setattr(workout_plan, field, value)
    workout_plan.save()
    return workout_plan