
from .services import MuscleService

from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import (
    MuscleGroupSerializer,
    MuscleCreateSerializer,
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