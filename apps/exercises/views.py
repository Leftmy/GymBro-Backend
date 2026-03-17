from rest_framework.views import APIView
from rest_framework.response import Response
from apps.exercises.services import get_exercises
from apps.exercises.serializers import ExerciseSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.exercises.services import get_exercises
from apps.exercises.serializers import ExerciseSerializer


class ExercisesAPIView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="muscle",
                description="Slug muscle groups (example: biceps)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="primary",
                description="Only primary muscles (true/false)",
                required=False,
                type=bool,
            ),
        ],
        responses=ExerciseSerializer(many=True),
    )
    def get(self, request):
        primary_param = request.query_params.get('primary')
        only_primary = True if primary_param == 'true' else False
        exercises = get_exercises(
            muscle_slug=request.query_params.get('muscle'),
            only_primary=only_primary
        )

        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data)

class ExerciseDetailAPIView(APIView):
    pass