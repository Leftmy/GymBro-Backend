from operator import add
from apps.users.models import User
from apps.exercises.models.exercise import Exercise
from apps.exercises.models.muscle_group import MuscleGroup
from apps.exercises.models.exercise_muscle_group import ExerciseMuscleGroup

from apps.workouts.models.workout_plan import WorkoutPlan
from apps.workouts.models.workout_plan_exercise import WorkoutPlanExercise
from apps.workouts.models.user_workout_plan import UserWorkoutPlan

from django.core.management.base import BaseCommand
from django.db import connection, transaction, DatabaseError


class Command(BaseCommand):
    help = 'Seeds the database with initial data'
    def add_arguments(self, parser):
            parser.add_argument('--force', action='store_true', help='Reset the database before seeding')

    @transaction.atomic
    def handle(self, *args, **options):

        self.force = options['force']
        if self.force:
            self.reset_database()
        
       
        self.seed_users()
        self.seed_exercises()
        self.seed_muscle_groups()
        self.seed_exercise_muscle_groups()
        self.seed_workout_plans()
        self.seed_workout_plan_exercises()
        self.seed_user_workout_plans()

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))


    def seed_users(self):
        self.stdout.write("Seeding users...")

        users_data = [
            {"username": "john_doe", "email": "john@example.com", "password": "password123", "is_admin": False},
            {"username": "jane_doe", "email": "jane@example.com", "password": "jane12345", "is_admin": False},
            {"username": "admin", "email": "admin@example.com", "password": "admin12345", "is_admin": True},
        ]

        self.users = {}

        for udata in users_data:
            try:
                user = User.objects.get(username=udata["username"])
                self.stdout.write(self.style.WARNING(f"User already exists: {user.username}"))
            except User.DoesNotExist:
                if udata["is_admin"]:
                    user = User.objects.create_superuser(
                        username=udata["username"],
                        email=udata["email"],
                        password=udata["password"],
                    )
                else:
                    user = User.objects.create_user(
                        username=udata["username"],
                        email=udata["email"],
                        password=udata["password"],
                    )
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))

            self.users[udata["username"]] = user

    def seed_exercises(self):
        exercises_data = [
            ("Push-Up", "A bodyweight exercise that primarily targets the chest, triceps, and shoulders.", "https://www.youtube.com/watch?v=_l3ySVKYVJ8"),
            ("Squat", "A compound exercise that primarily targets the quadriceps, hamstrings, glutes, and lower back.", "https://www.youtube.com/watch?v=aclHkVaku9U"),
            ("Deadlift", "A compound exercise that primarily targets the hamstrings, glutes, lower back, and traps.", "https://www.youtube.com/watch?v=op9kVnSso6Q"),
        ]   
        Exercise.objects.bulk_create([
            Exercise(name=name, description=description, video_url=video_url)
            for name, description, video_url in exercises_data
        ], ignore_conflicts=True)
        
    def seed_muscle_groups(self):
        muscle_groups_data = [
            ("Chest",),
            ("Back",),
            ("Legs",),
            ("Arms",),
            ("Shoulders",),
        ]
        MuscleGroup.objects.bulk_create([
            MuscleGroup(name=name)
            for name, in muscle_groups_data
        ], ignore_conflicts=True)
        
    def seed_exercise_muscle_groups(self):
        exercises = {e.name: e for e in Exercise.objects.all()}
        muscles = {m.name: m for m in MuscleGroup.objects.all()}

        relations = {
            "Push-Up": ["Chest", "Arms", "Shoulders"],
            "Squat": ["Legs"],
            "Deadlift": ["Legs", "Back"],
        }

        for ex_name, muscle_list in relations.items():
            for muscle_name in muscle_list:
                ExerciseMuscleGroup.objects.get_or_create(
                    exercise=exercises[ex_name],
                    muscle_group=muscles[muscle_name]
                )

    def seed_workout_plans(self):
        workout_plans_data = [
            ("Beginner Full Body", "A workout plan designed for beginners that targets all major muscle groups."),
            ("Upper Body Strength", "A workout plan focused on building upper body strength, targeting the chest, back, shoulders, and arms."),
            ("Lower Body Strength", "A workout plan focused on building lower body strength, targeting the legs and glutes."),
        ]
        WorkoutPlan.objects.bulk_create([
            WorkoutPlan(name=name, description=description)
            for name, description in workout_plans_data
        ], ignore_conflicts=True)

    def seed_workout_plan_exercises(self):
        self.stdout.write("Seeding workout plan exercises...")

        plans = {p.name: p for p in WorkoutPlan.objects.all()}
        exercises = {e.name: e for e in Exercise.objects.all()}

        workout_plan_exercises_data = {
            "Beginner Full Body": [
                ("Push-Up", 3, 12),
                ("Squat", 3, 15),
            ],
            "Upper Body Strength": [
                ("Push-Up", 4, 15),
                ("Deadlift", 4, 10),
            ],
            "Lower Body Strength": [
                ("Squat", 5, 15),
                ("Deadlift", 5, 12),
            ],
        }

        for plan_name, exercise_list in workout_plan_exercises_data.items():
            for exercise_name, sets, reps in exercise_list:
                WorkoutPlanExercise.objects.get_or_create(
                    workout_plan=plans[plan_name],
                    exercise=exercises[exercise_name],
                    defaults={"sets": sets, "reps": reps},
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added {exercise_name} to {plan_name} ({sets} sets)"
                    )
                )
    def seed_user_workout_plans(self):
        self.stdout.write("Seeding user workout plans...")

        users = {u.username: u for u in User.objects.all()}
        plans = {p.name: p for p in WorkoutPlan.objects.all()}

        user_workout_plans_data = {
            "john_doe": ["Beginner Full Body", "Upper Body Strength"],
            "jane_doe": ["Beginner Full Body"],
            "admin": ["Lower Body Strength"],
        }

        for username, plan_list in user_workout_plans_data.items():
            for plan_name in plan_list:
                UserWorkoutPlan.objects.get_or_create(
                    user=users[username],
                    workout_plan=plans[plan_name],
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Assigned {plan_name} to {username}"
                    )
                )
    def reset_database(self):
        self.stdout.write(self.style.WARNING("Cleaning existing data..."))
        models_to_clear = [User, Exercise, MuscleGroup, ExerciseMuscleGroup, WorkoutPlan, WorkoutPlanExercise, UserWorkoutPlan]
        for model in models_to_clear:
            model.objects.all().delete()

        self.reset_auto_increment()

    def reset_auto_increment(self):
        with connection.cursor() as cursor:
            tables = ['users', 'exercises', 'muscle_groups', 'exercise_muscle_groups', 'workout_plans', 'workout_plan_exercises', 'user_workout_plans']
            for table in tables:
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
