"""
URL patterns for the users app.

All routes are included under /api/v1/ via the project-level urls.py.
Auth endpoints are rate-limited (5/minute) via ScopedRateThrottle.

Auth routes:
  POST  auth/token/            — obtain access + refresh JWT (custom claims)
  POST  auth/token/refresh/    — rotate refresh token, get new access token
  POST  auth/token/blacklist/  — logout / blacklist refresh token
  POST  auth/register/         — register a new user account
  POST  auth/password/reset/   — initiate password reset flow

Profile routes:
  GET/PATCH/DELETE  me/        — manage the authenticated user's own profile
  GET               search/    — search users by username prefix
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .tokens import GymBroTokenObtainPairView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    UserView,
    UserSearchAPIView,
)

urlpatterns = [
    # -----------------------------------------------------------------------
    # Authentication
    # -----------------------------------------------------------------------
    # POST — obtain access + refresh token pair (custom claims: user_uuid, email, role)
    path("auth/token/", GymBroTokenObtainPairView.as_view(), name="token-obtain"),

    # POST — refresh the access token using a valid refresh token (rotation enabled)
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # POST — blacklist the refresh token (logout)
    path("auth/token/blacklist/", LogoutView.as_view(), name="token-blacklist"),

    # POST — register a new user account
    path("auth/register/", RegisterView.as_view(), name="register-user"),

    # Legacy login alias kept for backward-compat; points to the same JWT view
    path("auth/login/", LoginView.as_view(), name="login-user"),

    # POST — initiate password reset flow (email-based)
    path("auth/password/reset/", PasswordResetRequestView.as_view(), name="password-reset"),

    # -----------------------------------------------------------------------
    # Profile
    # -----------------------------------------------------------------------
    # GET / PATCH / DELETE — manage the authenticated user's own profile
    path("me/", UserView.as_view(), name="manage-user"),

    # GET ?search=<query> — search users by username prefix
    path("search/", UserSearchAPIView.as_view(), name="search-users"),
]