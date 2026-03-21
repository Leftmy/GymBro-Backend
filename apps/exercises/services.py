from typing import Optional
from django.db import transaction
from apps.exercises.models.exercise import Exercise
from apps.exercises.models.muscle_group import MuscleGroup
from apps.exercises.models.exercise_muscle_group import ExerciseMuscle

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
    
class ExerciseService:
    @staticmethod
    def get_all_exercises(*, muscle_slug: str = None, only_primary: bool = False, difficulty: int = None, equipment: str = None ):

        qs = Exercise.objects.all()

        if muscle_slug:
            qs = qs.filter(muscle_links__muscle__slug=muscle_slug, muscle_links__is_primary=only_primary)
        
            # if only_primary:
            #     qs = qs.filter(muscle_links__is_primary=True)

        if difficulty:
            qs = qs.filter(difficulty=difficulty)

        if equipment:
            qs = qs.filter(equipment=equipment)

        return qs.distinct()
    
    @staticmethod
    def get_exercise_by_id(exercise_id: int):
        return Exercise.objects.filter(id=exercise_id).first()
        
    @staticmethod
    def get_exercise_by_name(exercise_name: str):
        return Exercise.objects.filter(name=exercise_name).first()
    
    @staticmethod
    def create_exercise(
        *, 
        name: str, 
        slug: str = None, 
        description: str = "", 
        video_url: str = "", 
        difficulty: int = 1, 
        equipment: str = "", 
        muscles_map: list[dict]
    ):
        if ExerciseService.get_exercise_by_name(name):
            return None

        with transaction.atomic():
            exercise = Exercise.objects.create(
                name=name,
                slug=slug, 
                description=description,
                video_url=video_url,
                difficulty=difficulty,
                equipment=equipment
            )

            for item in muscles_map:
                muscle_slug = item.get('slug')
                is_primary = item.get('is_primary', False)

                muscle = MuscleGroup.objects.filter(slug=muscle_slug).first()
                
                if muscle:
                    ExerciseMuscle.objects.create(
                        exercise=exercise,
                        muscle=muscle,
                        is_primary=is_primary
                    )
            
            return exercise

    @staticmethod
    def update_exercise(exercise_id, **data):
        exercise = ExerciseService.get_exercise_by_id(exercise_id)

        if not exercise:
            return None

        muscles_map = data.pop('muscles_map', None)

        with transaction.atomic():
            for attr, value in data.items():
                setattr(exercise, attr, value)
            exercise.save()

            if muscles_map is not None:
                exercise.muscle_links.all().delete()

                for item in muscles_map:
                    muscle_slug = item.get('slug')
                    is_primary = item.get('is_primary', False)

                    muscle = MuscleGroup.objects.filter(slug=muscle_slug).first()
                    if muscle:
                        ExerciseMuscle.objects.create(
                            exercise=exercise,
                            muscle=muscle,
                            is_primary=is_primary
                        )
            
            return exercise
        

    @staticmethod
    def delete_exercise(exercise_id: int):
        exercise = ExerciseService.get_exercise_by_id(exercise_id)

        if not exercise:
            return False
        
        exercise.delete()
        return True
