from rest_framework import serializers
from .models import WorkoutPlan

class WorkoutPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutPlan
        fields = ['id', 'name', 'description', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_at']