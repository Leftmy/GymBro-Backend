from apps.exercises.models.exercise import Exercise
from apps.exercises.models.exercise_muscle_group import ExerciseMuscleGroup


from django.db.models import Prefetch

# def get_exercises(muscle_slug=None, only_primary=None):
#     return ExerciseMuscleGroup.objects.filter(muscle_group__slug=muscle_slug,is_primary=only_primary).values('exercise_id', 'muscle_group__slug', 'is_primary')
def get_exercises(muscle_slug=None, only_primary=None):
    qs = Exercise.objects.filter(
        exercise_muscles__muscle_group__slug=muscle_slug,
        exercise_muscles__is_primary=only_primary
    ).distinct()

    return qs