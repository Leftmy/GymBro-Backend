import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from apps.users.models import UserRole
from apps.exercises.models import MuscleGroup, Exercise, ExerciseMuscleGroup
from apps.workouts.models import WorkoutPlan, WorkoutPlanExercise, UserWorkoutPlan

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with realistic fitness data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')

        # --- 1. Користувачі ---
        self.stdout.write('Creating users...')
        users_data = [
            {'username': 'admin', 'email': 'admin@gymbro.com', 'role': UserRole.ADMIN, 'password': 'admin123', 'is_staff': True, 'is_superuser': True},
            {'username': 'trainer_john', 'email': 'john@gymbro.com', 'role': UserRole.TRAINER, 'password': 'trainer123'},
            {'username': 'client_alex', 'email': 'alex@gymbro.com', 'role': UserRole.CLIENT, 'password': 'client123'},
        ]
        users = {}
        for udata in users_data:
            user, _ = User.objects.get_or_create(
                username=udata['username'],
                defaults={
                    'email': udata['email'],
                    'role': udata['role'],
                    'is_staff': udata.get('is_staff', False),
                    'is_superuser': udata.get('is_superuser', False)
                }
            )
            user.set_password(udata['password'])
            user.save()
            users[udata['username']] = user

        # --- 2. М'язові групи ---
        self.stdout.write('Creating muscle groups...')
        muscles_data = [
            ('Chest', 'muscle-chest'),
            ('Back', 'muscle-back'),
            ('Biceps', 'muscle-biceps'),
            ('Triceps', 'muscle-triceps'),
            ('Quads', 'muscle-quads'),
            ('Abs', 'muscle-abs'),
            ('Shoulders', 'muscle-shoulders'),
        ]
        muscle_objs = {}
        for name, svg in muscles_data:
            mg, _ = MuscleGroup.objects.get_or_create(
                name=name,
                defaults={'svg_id': svg, 'slug': slugify(name)}
            )
            muscle_objs[name] = mg

        # --- 3. Вправи ---
        self.stdout.write('Creating exercises...')
        exercises_info = [
            {'name': 'Bench Press', 'difficulty': Exercise.Difficulty.INTERMEDIATE, 'primary': ['Chest'], 'secondary': ['Triceps', 'Shoulders']},
            {'name': 'Deadlift', 'difficulty': Exercise.Difficulty.ADVANCED, 'primary': ['Back'], 'secondary': ['Quads']},
            {'name': 'Push-ups', 'difficulty': Exercise.Difficulty.BEGINNER, 'primary': ['Chest'], 'secondary': ['Triceps']},
            {'name': 'Bicep Curls', 'difficulty': Exercise.Difficulty.BEGINNER, 'primary': ['Biceps'], 'secondary': []},
            {'name': 'Plank', 'difficulty': Exercise.Difficulty.BEGINNER, 'primary': ['Abs'], 'secondary': []},
        ]

        exercise_objs = []
        for ex_data in exercises_info:
            exercise, _ = Exercise.objects.get_or_create(
                name=ex_data['name'],
                defaults={'difficulty_level': ex_data['difficulty']}
            )
            exercise_objs.append(exercise)

            # --- Очищаємо старі зв’язки ---
            ExerciseMuscleGroup.objects.filter(exercise=exercise).delete()

            bulk_data = []
            # Primary
            for m in ex_data['primary']:
                bulk_data.append(ExerciseMuscleGroup(exercise=exercise, muscle_group=muscle_objs[m], is_primary=True))
            # Secondary
            for m in ex_data['secondary']:
                bulk_data.append(ExerciseMuscleGroup(exercise=exercise, muscle_group=muscle_objs[m], is_primary=False))

            ExerciseMuscleGroup.objects.bulk_create(bulk_data)

        # --- 4. Плани тренувань ---
        self.stdout.write('Creating workout plans...')
        plan_names = ['Full Body Beginner', 'Push Day (Advanced)']
        for plan_name in plan_names:
            plan, created = WorkoutPlan.objects.get_or_create(
                name=plan_name,
                defaults={'created_by': users['trainer_john'], 'description': f'A great {plan_name} routine.'}
            )

            if created:
                selected_exercises = random.sample(exercise_objs, 3)
                bulk_plan_exercises = []
                for i, ex in enumerate(selected_exercises):
                    bulk_plan_exercises.append(
                        WorkoutPlanExercise(
                            workout_plan=plan,
                            exercise=ex,
                            sets=3,
                            reps=12,
                            rest_seconds=60,
                            order=i + 1
                        )
                    )
                WorkoutPlanExercise.objects.bulk_create(bulk_plan_exercises)

        # --- 5. Призначення плану користувачу ---
        self.stdout.write('Assigning plans to users...')
        first_plan = WorkoutPlan.objects.first()
        if first_plan:
            UserWorkoutPlan.objects.get_or_create(
                user=users['client_alex'],
                workout_plan=first_plan,
                defaults={'is_active': True}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))