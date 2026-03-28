from rest_framework import serializers

from apps.exercises.serializers import ExerciseSerializer
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