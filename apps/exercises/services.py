from apps.exercises.models.exercise import Exercise
from apps.exercises.models.exercise_muscle_group import ExerciseMuscleGroup
from apps.exercises.models.muscle_group import MuscleGroup

# def get_exercises(muscle_slug=None, only_primary=None):
#     return ExerciseMuscleGroup.objects.filter(muscle_group__slug=muscle_slug,is_primary=only_primary).values('exercise_id', 'muscle_group__slug', 'is_primary')
def get_exercises(muscle_slug=None, only_primary=None):
    qs = Exercise.objects.filter(
        exercise_muscles__muscle_group__slug=muscle_slug,
        exercise_muscles__is_primary=only_primary
    ).distinct()

    return qs

class MuscleService:
    @staticmethod
    def get_muscles_by_name(muscle_name: str):
        if muscle_name is not None:
            return MuscleGroup.objects.get(name=muscle_name)
        
        return None
    
    @staticmethod
    def get_muscles_by_id(muscle_id: int):
        if muscle_id is not None:
            return MuscleGroup.objects.get(id=muscle_id)
        
        return None

    @staticmethod
    def create_muscle(*, name: str, slug: str, svg_id: int):
        muscle = MuscleGroup.get_muscles_by_name(name)
        if muscle is not None:
            return None
        
        return MuscleGroup.objects.create(name=name, slug=slug, svg_id=svg_id)

    @staticmethod
    def update_muscle(muscle_id: int, **data):
        muscle = MuscleService.get_muscles_by_id(muscle_id)
        if muscle is None:
            return None
        
        for attr, value in data.items():
            setattr(muscle, attr, value)
                
        muscle.save()
        return muscle
    
    @staticmethod
    def delete_muscle(muscle_id) -> bool:
        muscle = MuscleService.get_muscles_by_id(muscle_id)

        if muscle is None:
            return None
        
        return MuscleGroup.objects.delete(muscle)