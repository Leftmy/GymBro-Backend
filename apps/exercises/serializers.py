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
    difficulty = serializers.CharField(source='get_difficulty_level_display')
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