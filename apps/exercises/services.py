from typing import Optional

from apps.exercises.models.exercise import Exercise
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
    def get_all_muscles():
        return MuscleGroup.objects.all()

    @staticmethod
    def get_muscle_by_id(muscle_id: int) -> Optional[MuscleGroup]:
        return MuscleGroup.objects.filter(id=muscle_id).first()

    @staticmethod
    def get_muscles_by_name(name: str) -> Optional[MuscleGroup]:
        return MuscleGroup.objects.filter(name=name).first()

    @staticmethod
    def create_muscle(**data):
        if MuscleGroup.objects.filter(name=data.get('name')).exists():
            return None
        return MuscleGroup.objects.create(**data)

    @staticmethod
    def update_muscle(muscle_id: int, data: dict):
        muscle = MuscleService.get_muscle_by_id(muscle_id)
        if not muscle:
            return None
        
        for attr, value in data.items():
            setattr(muscle, attr, value)
        muscle.save()
        return muscle
    
    @staticmethod
    def delete_muscle(muscle_id: int) -> bool:
        muscle = MuscleService.get_muscle_by_id(muscle_id)
        if muscle:
            muscle.delete()
            return True
        return False