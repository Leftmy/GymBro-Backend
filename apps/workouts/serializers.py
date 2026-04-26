from rest_framework import serializers

from apps.exercises.serializers import ExerciseSerializer
from apps.workouts.models.user_workout_plan import UserWorkoutPlan
from apps.workouts.models.workout_plan import WorkoutPlan
from apps.workouts.models.workout_plan_exercise import WorkoutPlanExercise


# ------------------------
# 🔹 READ SERIALIZERS
# ------------------------

class WorkoutPlanExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer()

    class Meta:
        model = WorkoutPlanExercise
        fields = ["exercise", "sets", "reps", "rest_seconds", "order"]


class WorkoutPlanSerializer(serializers.ModelSerializer):
    exercises = WorkoutPlanExerciseSerializer(
        source="plan_exercises",
        many=True
    )

    class Meta:
        model = WorkoutPlan
        fields = [
            "id",
            "name",
            "description",
            "is_public",
            "exercises",
        ]

class UserWorkoutPlanReadSerializer(serializers.ModelSerializer):
    workout = WorkoutPlanSerializer(source="workout_plan")

    class Meta:
        model = UserWorkoutPlan
        fields = [
            "id",
            "day_of_week",
            "is_active",
            "workout",
        ]

# ------------------------
# 🔹 WRITE SERIALIZERS
# ------------------------

class WorkoutExerciseMapSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    sets = serializers.IntegerField(min_value=1)
    reps = serializers.IntegerField(min_value=1)
    rest_seconds = serializers.IntegerField(min_value=0, required=False, default=60)
    order = serializers.IntegerField(min_value=1)


class ValidateWorkoutExercisesMixin:
    def validate_exercises(self, value):
        if not value:
            return value

        # 🔹 order validation
        orders = [item["order"] for item in value]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("Order must be unique")

        # 🔹 slug duplicates
        slugs = [item["slug"] for item in value]
        if len(slugs) != len(set(slugs)):
            raise serializers.ValidationError("Duplicate exercises")

        return value
    
class UserWorkoutPlanWriteSerializer(serializers.Serializer):
    workout_plan_id = serializers.IntegerField(required=False)
    day_of_week = serializers.ChoiceField(
        choices=UserWorkoutPlan._meta.get_field("day_of_week").choices,
        required=False,
        allow_null=True
    )
    is_active = serializers.BooleanField(required=False)

    def validate(self, data):
        user = self.context["request"].user

        day = data.get("day_of_week")

        if day is not None:
            qs = UserWorkoutPlan.objects.filter(
                user=user,
                day_of_week=day
            )

            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError({
                    "day_of_week": "You already have a workout for this day"
                })

        return data


class WorkoutCreateSerializer(ValidateWorkoutExercisesMixin, serializers.Serializer):
    name = serializers.CharField(trim_whitespace=True)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(default=False)
    exercises = WorkoutExerciseMapSerializer(many=True)


class WorkoutUpdateSerializer(ValidateWorkoutExercisesMixin, serializers.Serializer):
    name = serializers.CharField(required=False, trim_whitespace=True)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(required=False)
    exercises = WorkoutExerciseMapSerializer(many=True, required=False)