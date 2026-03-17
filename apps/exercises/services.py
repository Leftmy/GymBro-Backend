from apps.exercises.models.exercise import Exercise


def get_exercises(muscle_slug=None, only_primary=None):
    qs = Exercise.objects.all()

    if muscle_slug:
        filter_kwargs = {'exercise_muscles__muscle_group__slug': muscle_slug}
        
        if only_primary is not None:
            filter_kwargs['exercise_muscles__is_primary'] = only_primary
            
        qs = qs.filter(**filter_kwargs)

    return qs.prefetch_related('muscles').distinct()

def get_exercises_by_muscle(slug):
    return Exercise.objects.filter(
        exercise_muscles__muscle_group__slug=slug
    ).select_related().prefetch_related(
        'muscles',
        'exercise_muscles'
    ).distinct()

def get_exercises(muscle_slug=None, only_primary=False):
    qs = Exercise.objects.all()

    if muscle_slug:
        qs = qs.filter(
            exercise_muscles__muscle_group__slug=muscle_slug
        )

        if only_primary:
            qs = qs.filter(exercise_muscles__is_primary=True)

    return qs.prefetch_related('muscles').distinct()