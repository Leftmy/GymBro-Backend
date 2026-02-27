from apps.exercises.models import (
    Exercise,
    ExerciseMuscleGroup,
    MuscleGroup
)

def get_all_exercises():
    return Exercise.objects.all()

def get_all_muscle_groups():
    return MuscleGroup.objects.all()

def get_all_exercises_by_muscle_group(muscle_group_name: str):
    if not muscle_group_name or muscle_group_name.strip() == "":
        return Exercise.objects.none()
    
    return Exercise.objects.filter(
        id__in=ExerciseMuscleGroup.objects.filter(
            muscle_group__name=muscle_group_name
        ).values_list('exercise_id', flat=True)
    )