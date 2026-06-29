"""
User-related API views.

Auth endpoints (register, login, logout, refresh, password-reset) live under
/api/v1/auth/ and are rate-limited via the 'auth' throttle scope (5 req/min).
Profile endpoints (me, search) are protected by JWT IsAuthenticated.
"""

from rest_framework import status
from rest_framework.views import APIView, Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from drf_spectacular.utils import OpenApiParameter, extend_schema

from .serializers import (
    UserUpdateSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
)
from .services import UserService


# ---------------------------------------------------------------------------
# Auth: throttle scope applied to all auth endpoints
# ---------------------------------------------------------------------------

class RegisterView(APIView):
    """POST /api/v1/auth/register/ — create a new user account."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        validated_data.pop("password_confirm", None)

        user = UserService.create_user(**validated_data)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/v1/auth/token/ — obtain an access + refresh JWT pair.

    Custom claims embedded in the access token: user_uuid, email, role.
    Rate-limited to 5 requests/minute per IP.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: dict},
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_data = UserService.authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "access": auth_data["access"],
                "refresh": auth_data["refresh"],
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/v1/auth/token/blacklist/ — invalidate (blacklist) the refresh token.

    Requires a valid refresh token in the request body.
    The corresponding access token will be unusable once the refresh is blacklisted.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        request={"application/json": {"type": "object", "properties": {"refresh": {"type": "string"}}}},
        responses={205: None, 400: dict},
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_205_RESET_CONTENT)


class PasswordResetRequestView(APIView):
    """
    POST /api/v1/auth/password/reset/ — initiate a password reset flow.

    Validates the email and (in a production setup) would enqueue an email
    with a reset link.  Returns 200 regardless of whether the email exists
    to prevent user-enumeration attacks.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: dict},
    )
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # NOTE: actual email dispatch is wired up in the notifications app (Issue #12).
        # Here we intentionally return 200 even if the email is unknown to avoid
        # leaking registered addresses (user-enumeration protection).

        return Response(
            {"detail": "If this email is registered, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Profile endpoints (require authentication)
# ---------------------------------------------------------------------------

class UserSearchAPIView(APIView):
    """GET /api/v1/users/search/?search=<query> — full-text user search."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                required=True,
                description="Search users by username",
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                required=False,
                description="Number of results (default 10, max 20)",
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                required=False,
                description="Pagination offset",
            ),
        ],
        responses={200: UserSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("search", "").strip()

        # Basic protection: ignore queries shorter than 2 characters
        if len(query) < 2:
            return Response([], status=status.HTTP_200_OK)

        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10

        try:
            offset = int(request.query_params.get("offset", 0))
        except (TypeError, ValueError):
            offset = 0

        users = UserService.search_users(query=query, limit=limit, offset=offset)
        return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)


class UserView(APIView):
    """GET / PATCH / DELETE /api/v1/users/me/ — manage the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request, *args, **kwargs):
        """Retrieve current user's data."""
        return Response(UserSerializer(request.user).data)

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
    )
    def patch(self, request, *args, **kwargs):
        """Update current user's profile."""
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.update_user(
            user_id=request.user.id,
            **serializer.validated_data,
        )

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, *args, **kwargs):
        """Delete current user's profile."""
        UserService.delete_user(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)