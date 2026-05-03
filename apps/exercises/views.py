
from .services import MuscleService, ExerciseService

from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ViewSet
from .serializers import (
    MuscleGroupSerializer,
    MuscleCreateSerializer,
    ExerciseCreateSerializer,
    ExerciseSerializer
)

class MusclesView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, description='Filter by ID'),
            OpenApiParameter(name='name', type=str, description='Filter by name'),
        ],
        responses={200: MuscleGroupSerializer(many=True)}
    )
    def get(self, request):
        muscle_id = request.query_params.get('id')
        muscle_name = request.query_params.get('name')

        if muscle_id:
            muscle = MuscleService.get_muscle_by_id(muscle_id)
            if not muscle: return Response(status=404)
            return Response(MuscleGroupSerializer(muscle).data)
        
        if muscle_name:
            muscle = MuscleService.get_muscles_by_name(muscle_name)
            if not muscle: return Response(status=404)
            return Response(MuscleGroupSerializer(muscle).data)

        muscles = MuscleService.get_all_muscles()
        return Response(MuscleGroupSerializer(muscles, many=True).data)
    

    @extend_schema(request=MuscleCreateSerializer, responses={201: MuscleGroupSerializer})
    def post(self, request):
        serializer = MuscleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        muscle = MuscleService.create_muscle(**serializer.validated_data)
        if not muscle:
            return Response({"detail": "М'яз з такою назвою вже існує"}, status=400)
            
        return Response(MuscleGroupSerializer(muscle).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=int)],
        request=MuscleCreateSerializer, 
        responses={202: MuscleGroupSerializer}
    )
    def patch(self, request):
        m_id = request.query_params.get('id')
        if not m_id:
            return Response({"detail": "ID is required"}, status=400)

        serializer = MuscleCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        muscle = MuscleService.update_muscle(int(m_id), serializer.validated_data)
        
        if not muscle:
            return Response({"detail": "М'яз не знайдено"}, status=404)
            
        return Response(MuscleGroupSerializer(muscle).data, status=status.HTTP_202_ACCEPTED)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, description='Filter by ID'),
        ],
        responses={204}
    )
    def delete(self, request):
        m_id = request.query_params.get('id')
        if not m_id:
            return Response({"detail": "ID is required"}, status=400)
        
        success = MuscleService.delete_muscle(int(m_id))
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response({"detail": "Muscle not found"}, status=404)
    

class ExerciseView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, description='Filter by ID'),
            OpenApiParameter(name='name', type=str, description='Filter by name'),
            OpenApiParameter(name='muscle', type=str, description='Filter by muscle slug'),
            OpenApiParameter(name='primary', type=bool, description='Additional filter for muscles'),
            OpenApiParameter(name='difficulty', type=int, description='Filter by difficulty level'),
            OpenApiParameter(name='equipment', type=str, description='Filter by equipment slug'),
        ],
        responses={200: ExerciseSerializer(many=True)}
    )
    def get(self, request):
        exercise_id = request.query_params.get('id')

        if exercise_id:
            exercise = ExerciseService.get_exercise_by_id(exercise_id)
            if not exercise: return Response(status=404)
            return Response(ExerciseSerializer(exercise).data)
        
        exercise_name = request.query_params.get('name')
        if exercise_name:
            exercise = ExerciseService.get_exercise_by_name(exercise_name)
            if not exercise: return Response(status=404)
            return Response(ExerciseSerializer(exercise).data)
        
        primary_param = request.query_params.get('primary')

        if primary_param is None:
            only_primary = None
        else:
            only_primary = primary_param.lower() == 'true'
        exercises = ExerciseService.get_all_exercises(
            muscle_slug=request.query_params.get('muscle'),
            only_primary=only_primary,
            difficulty=request.query_params.get('difficulty'),
            equipment=request.query_params.get('equipment')
        )
        return Response(ExerciseSerializer(exercises, many=True).data)
    
    @extend_schema(request=ExerciseCreateSerializer, responses={201: ExerciseSerializer})
    def post(self, request):
        serializer = ExerciseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        exercise = ExerciseService.create_exercise(**serializer.validated_data)
        if not exercise:
            return Response({"detail": "Вправа з такою назвою вже існує"}, status=400)
            
        return Response(ExerciseSerializer(exercise).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=int)],
        request=ExerciseCreateSerializer, 
        responses={200: ExerciseSerializer}
    )
    def patch(self, request):
        m_id = request.query_params.get('id')
        if not m_id:
            return Response({"detail": "ID is required"}, status=400)

        serializer = ExerciseCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        exercise = ExerciseService.update_exercise(int(m_id), **serializer.validated_data)
        
        if not exercise:
            return Response({"detail": "М'яз не знайдено"}, status=404)
            
        return Response(ExerciseSerializer(exercise).data, status=status.HTTP_200_ACCEPTED)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, description='Filter by ID'),
        ],
        responses={204}
    )
    def delete(self, request):
        m_id = request.query_params.get('id')
        if not m_id:
            return Response({"detail": "ID is required"}, status=400)
        
        success = ExerciseService.delete_exercise(int(m_id))
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response({"detail": "Muscle not found"}, status=404)