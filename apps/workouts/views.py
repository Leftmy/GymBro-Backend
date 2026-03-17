import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import status
from .serializers import WorkoutPlanSerializer
from apps.workouts.services import (
    get_all_workout_plans, 
    get_workout_plan_by_id, 
    create_workout_plan, 
    update_workout_plan,
    delete_workout
)

logger = logging.getLogger(__name__)


# TODO: Replace created_by with user id
class PlansAPIView(APIView):
    def get(self, request):
        workouts = get_all_workout_plans()
        serializer = WorkoutPlanSerializer(workouts, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=WorkoutPlanSerializer,
        responses={201: WorkoutPlanSerializer}
    )
    def post(self, request):
        serializer = WorkoutPlanSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        workout = create_workout_plan(
            name=validated_data['name'],
            description=validated_data.get('description'),
            created_by=request.user
        )
        
        output_serializer = WorkoutPlanSerializer(workout)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


# TODO: Remove created_by from PATCH
class PlansDetailsAPIView(APIView):
    def get(self, request, pk):
        workout = get_workout_plan_by_id(pk)
        serializer = WorkoutPlanSerializer(workout)
        return Response(serializer.data)
    
    @extend_schema(
        request=WorkoutPlanSerializer,
        responses={200: WorkoutPlanSerializer}
    )
    def patch(self, request, pk):
        workout = get_workout_plan_by_id(pk)
        
        serializer = WorkoutPlanSerializer(workout, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_workout = update_workout_plan(workout, **serializer.validated_data)
        
        return Response(WorkoutPlanSerializer(updated_workout).data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        deleted = delete_workout(pk)

        if not deleted:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)