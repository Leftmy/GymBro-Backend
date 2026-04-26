from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from drf_spectacular.utils import OpenApiParameter, extend_schema, OpenApiResponse, OpenApiExample

from apps.workouts.models.user_workout_plan import UserWorkoutPlan
from apps.workouts.models.workout_plan import WorkoutPlan
from apps.workouts.services import WorkoutService
from apps.workouts.serializers import (
    UserWorkoutPlanReadSerializer,
    UserWorkoutPlanWriteSerializer,
    WorkoutPlanSerializer,
    WorkoutCreateSerializer,
    WorkoutUpdateSerializer,
)
class WorkoutsView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='day',
                type=str,
                enum=['all', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'], 
            ),
        ],
        summary="Get user workouts (optionally filtered by day)",
        responses=UserWorkoutPlanReadSerializer(many=True),
    )
    def get(self, request):
        day = request.query_params.get("day")

        user_workouts = WorkoutService.get_all_user_workouts(request.user)
        workouts = WorkoutService.filter_user_workouts_by_day(user_workouts, day)

        workouts = (
            workouts
            .select_related("workout_plan")
            .prefetch_related(
                "workout_plan__plan_exercises__exercise__muscles"
            )
        )

        return Response(
            UserWorkoutPlanReadSerializer(workouts, many=True).data
        )
    
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
    def post(self, request):
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
    
class WorkoutsDetailView(APIView):
    @extend_schema(
        summary="Get workout by ID",
        responses={
            200: WorkoutPlanSerializer,
            404: OpenApiResponse(description="Not found"),
        },
    )
    def get(self, request, pk=None):
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

    @extend_schema(
        summary="Update workout",
        request=WorkoutUpdateSerializer,
        responses=WorkoutPlanSerializer,
    )
    def patch(self, request, pk=None):
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
    def delete(self, request, pk=None):
        workout = WorkoutService.get_workout_by_id(pk)

        if not workout:
            return Response({"detail": "Not found"}, status=404)

        if workout.created_by != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        WorkoutService.delete_workout(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)
    

class UserWorkoutPlanView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Assign workout plan to user",
        description="Assign an existing workout plan to the authenticated user with optional day of week",
        request=UserWorkoutPlanWriteSerializer,
        responses={
            201: UserWorkoutPlanReadSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Workout not found"),
        },
        examples=[
            OpenApiExample(
                "Assign workout (Monday)",
                value={
                    "workout_plan_id": 1,
                    "day_of_week": 1,
                    "is_active": True
                },
                request_only=True,
            ),
            OpenApiExample(
                "Assign without day",
                value={
                    "workout_plan_id": 2,
                    "is_active": False
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = UserWorkoutPlanWriteSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        obj = WorkoutService.assign_workout_to_user(
            user=request.user,
            workout_plan_id=serializer.validated_data.get("workout_plan_id"),
            day_of_week=serializer.validated_data.get("day_of_week"),
            is_active=serializer.validated_data.get("is_active", True),
        )

        if not obj:
            return Response({"detail": "Workout not found"}, status=404)

        return Response(
            UserWorkoutPlanReadSerializer(obj).data,
            status=201
        )
    
class UserWorkoutPlanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update user workout plan",
        description="Update assigned workout (change day or active status)",
        request=UserWorkoutPlanWriteSerializer,
        responses={
            200: UserWorkoutPlanReadSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Not found"),
        },
        examples=[
            OpenApiExample(
                "Change day",
                value={
                    "day_of_week": 3
                },
                request_only=True,
            ),
            OpenApiExample(
                "Set as active",
                value={
                    "is_active": True
                },
                request_only=True,
            ),
        ],
    )
    def patch(self, request, pk):
        instance = UserWorkoutPlan.objects.filter(
            pk=pk,
            user=request.user
        ).first()

        if not instance:
            return Response({"detail": "Not found"}, status=404)

        serializer = UserWorkoutPlanWriteSerializer(
            instance=instance,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        updated = WorkoutService.update_user_workout_plan(
            instance,
            **serializer.validated_data
        )

        return Response(UserWorkoutPlanReadSerializer(updated).data)