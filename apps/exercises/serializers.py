from rest_framework import serializers
from apps.exercises.models import Exercise

        
class MuscleGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()

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