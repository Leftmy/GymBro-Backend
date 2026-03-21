from rest_framework import serializers
from apps.exercises.models import Exercise
from apps.exercises.models.muscle_group import MuscleGroup

        
class MuscleGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.SlugField()

class MuscleCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()
    svg_id = serializers.CharField()

class ExerciseSerializer(serializers.ModelSerializer):
    difficulty = serializers.CharField(source='get_difficulty_display')
    muscles = MuscleGroupSerializer(many=True)

    class Meta:
        model = Exercise
        fields = [
            'id',
            'name',
            'description',
            'difficulty',
            'muscles',
        ]

class ExerciseMuscleMapSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    is_primary = serializers.BooleanField(default=False)


class ExerciseCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    difficulty = serializers.IntegerField(default=1)
    equipment = serializers.CharField(required=False, allow_blank=True)
    video_url = serializers.URLField(required=False, allow_blank=True)
    muscles_map = ExerciseMuscleMapSerializer(many=True)

    def validate_muscles_map(self, value):
        slugs = [item["slug"] for item in value]

        if len(slugs) != len(set(slugs)):
            raise serializers.ValidationError("Duplicate muscles")

        return value