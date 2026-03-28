from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
    # 🔹 GET /workouts/
    # ------------------------
    def list(self, request):
        workouts = WorkoutService.get_all_user_workouts(request.user)

        # 🔥 оптимізація
        workouts = workouts.prefetch_related(
            "plan_exercises__exercise__muscles"
        )

        serializer = WorkoutPlanSerializer(workouts, many=True)
        return Response(serializer.data)

    # ------------------------
    # 🔹 GET /workouts/{id}/
    # ------------------------
    def retrieve(self, request, pk=None):
        workout = WorkoutService.get_workout_by_id(pk)

        if not workout:
            return Response({"detail": "Not found"}, status=404)

        # 🔐 базова безпека
        if workout.created_by != request.user and not workout.is_public:
            return Response({"detail": "Forbidden"}, status=403)

        workout = (
            WorkoutPlan.objects
            .filter(pk=pk)
            .prefetch_related("plan_exercises__exercise__muscles")
            .first()
        )

        serializer = WorkoutPlanSerializer(workout)
        return Response(serializer.data)

    # ------------------------
    # 🔹 POST /workouts/
    # ------------------------
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
    # 🔹 PATCH /workouts/{id}/
    # ------------------------
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
    # 🔹 DELETE /workouts/{id}/
    # ------------------------
    def destroy(self, request, pk=None):
        workout = WorkoutService.get_workout_by_id(pk)

        if not workout:
            return Response({"detail": "Not found"}, status=404)

        if workout.created_by != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        WorkoutService.delete_workout(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)