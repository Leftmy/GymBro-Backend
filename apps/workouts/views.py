from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from apps.workouts.models.workout_plan import WorkoutPlan
from apps.workouts.services import WorkoutService
from apps.workouts.serializers import (
    WorkoutPlanSerializer,
    WorkoutCreateSerializer,
    WorkoutUpdateSerializer,
)


class WorkoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # ------------------------
    # 🔹 LIST
    # ------------------------
    @extend_schema(
        summary="Get user workouts",
        responses=WorkoutPlanSerializer(many=True),
    )
    def list(self, request):
        workouts = WorkoutService.get_all_user_workouts(request.user)
        workouts = workouts.prefetch_related(
            "plan_exercises__exercise__muscles"
        )

        return Response(WorkoutPlanSerializer(workouts, many=True).data)

    # ------------------------
    # 🔹 RETRIEVE
    # ------------------------
    @extend_schema(
        summary="Get workout by ID",
        responses={
            200: WorkoutPlanSerializer,
            404: OpenApiResponse(description="Not found"),
        },
    )
    def retrieve(self, request, pk=None):
        workout = WorkoutService.get_workout_by_id(pk)

        if not workout:
            return Response({"detail": "Not found"}, status=404)

        if workout.created_by != request.user and not workout.is_public:
            return Response({"detail": "Forbidden"}, status=403)

        workout = (
            WorkoutPlan.objects
            .filter(pk=pk)
            .prefetch_related("plan_exercises__exercise__muscles")
            .first()
        )

        return Response(WorkoutPlanSerializer(workout).data)

    # ------------------------
    # 🔹 CREATE
    # ------------------------
    @extend_schema(
        summary="Create workout",
        request=WorkoutCreateSerializer,
        responses={
            201: WorkoutPlanSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Create workout example",
                value={
                    "name": "Leg Day",
                    "description": "Hard workout",
                    "is_public": False,
                    "exercises": [
                        {
                            "slug": "squat",
                            "sets": 4,
                            "reps": 10,
                            "rest_seconds": 90,
                            "order": 1
                        },
                        {
                            "slug": "lunges",
                            "sets": 3,
                            "reps": 12,
                            "order": 2
                        }
                    ]
                },
                request_only=True,
            )
        ],
    )
    def create(self, request):
        serializer = WorkoutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workout = WorkoutService.create_workout(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
            created_by=request.user,
            public=serializer.validated_data.get("is_public", False),
            exercises=serializer.validated_data["exercises"],
        )

        if not workout:
            return Response(
                {"detail": "Workout already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            WorkoutPlanSerializer(workout).data,
            status=status.HTTP_201_CREATED,
        )

    # ------------------------
    # 🔹 PATCH
    # ------------------------
    @extend_schema(
        summary="Update workout",
        request=WorkoutUpdateSerializer,
        responses=WorkoutPlanSerializer,
    )
    def partial_update(self, request, pk=None):
        serializer = WorkoutUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workout = WorkoutService.get_workout_by_id(pk)

        if not workout:
            return Response({"detail": "Not found"}, status=404)

        if workout.created_by != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        updated = WorkoutService.update_workout(
            pk, **serializer.validated_data
        )

        return Response(WorkoutPlanSerializer(updated).data)

    # ------------------------
    # 🔹 DELETE
    # ------------------------
    @extend_schema(
        summary="Delete workout",
        responses={
            204: OpenApiResponse(description="Deleted"),
            404: OpenApiResponse(description="Not found"),
        },
    )
    def destroy(self, request, pk=None):
        workout = WorkoutService.get_workout_by_id(pk)

        if not workout:
            return Response({"detail": "Not found"}, status=404)

        if workout.created_by != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        WorkoutService.delete_workout(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)