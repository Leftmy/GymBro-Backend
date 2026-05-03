from typing import Optional
from django.db import transaction
from apps.exercises.models.exercise import Exercise
from apps.exercises.models.muscle_group import MuscleGroup
from apps.exercises.models.exercise_muscle_group import ExerciseMuscle

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
    def get_all_exercises(
    *,
    muscle_slug: str = None,
    only_primary: bool = None,
    difficulty: int = None,
    equipment: str = None
    ):
        qs = Exercise.objects.prefetch_related("muscles").all()

        if muscle_slug:
            qs = qs.filter(muscle_links__muscle__slug=muscle_slug)

        if only_primary is not None:
            qs = qs.filter(muscle_links__is_primary=only_primary)

        if difficulty:
            qs = qs.filter(difficulty=difficulty)

        if equipment:
            qs = qs.filter(equipment=equipment)

        return qs.distinct()
    
    @staticmethod
    def get_exercise_by_id(exercise_id: int):
        return Exercise.objects.prefetch_related("muscles").filter(id=exercise_id).first()
        
    @staticmethod
    def get_exercise_by_name(exercise_name: str):
        return Exercise.objects.prefetch_related("muscles").filter(name=exercise_name).first()
    
    @staticmethod
    def create_exercise(*, name, description="", difficulty=1, equipment="", video_url="", muscles_map):
        from django.db import IntegrityError

        slugs = [m["slug"] for m in muscles_map]

        muscle_map = {
            m.slug: m for m in MuscleGroup.objects.filter(slug__in=slugs)
        }

        with transaction.atomic():
            try:
                exercise = Exercise.objects.create(
                    name=name,
                    description=description,
                    difficulty=difficulty,
                    equipment=equipment,
                    video_url=video_url,
                )
            except IntegrityError:
                return None

            links = []

            for item in muscles_map:
                muscle = muscle_map.get(item["slug"])
                if muscle:
                    links.append(
                        ExerciseMuscle(
                            exercise=exercise,
                            muscle=muscle,
                            is_primary=item.get("is_primary", False),
                        )
                    )

            ExerciseMuscle.objects.bulk_create(links)

            return exercise

    @staticmethod
    def update_exercise(exercise_id, **data):
        exercise = ExerciseService.get_exercise_by_id(exercise_id)

        if not exercise:
            return None

        muscles_map = data.pop("muscles_map", None)

        allowed_fields = {"name", "description", "video_url", "difficulty", "equipment"}

        with transaction.atomic():
            for attr, value in data.items():
                if attr in allowed_fields:
                    setattr(exercise, attr, value)

            exercise.save()

            if muscles_map is not None:
                exercise.muscle_links.all().delete()

                slugs = [item["slug"] for item in muscles_map]

                muscle_map = {
                    m.slug: m for m in MuscleGroup.objects.filter(slug__in=slugs)
                }

                links = []

                for item in muscles_map:
                    muscle = muscle_map.get(item["slug"])
                    if not muscle:
                        continue

                    links.append(
                        ExerciseMuscle(
                            exercise=exercise,
                            muscle=muscle,
                            is_primary=item.get("is_primary", False),
                        )
                    )

                ExerciseMuscle.objects.bulk_create(links)

            return exercise
        

    @staticmethod
    def delete_exercise(exercise_id: int):
        exercise = ExerciseService.get_exercise_by_id(exercise_id)

        if not exercise:
            return False
        
        exercise.delete()
        return True


    