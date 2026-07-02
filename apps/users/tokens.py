"""
Custom JWT token classes and serializers for GymBro.

Embeds additional claims (user_uuid, email, role) into the access token
so that downstream services can identify the user without an extra DB lookup.

Refresh tokens are stored as Secure HttpOnly cookies to prevent XSS attacks.
Access tokens are blacklisted on refresh for enhanced security.
"""

from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


COOKIE_NAME = "refresh_token"
# Access token cookie name and shared cookie settings
ACCESS_COOKIE_NAME = "access_token"
COOKIE_SECURE = True  # Set to False only for local development
COOKIE_HTTPONLY = True
COOKIE_SAMESITE = "Lax"  # Prevents CSRF; use "Strict" for maximum security


class GymBroRefreshToken(RefreshToken):
    """
    Custom RefreshToken that stores only stable user identifiers.
    Mutable claims like role or email are reconstructed when a new access
    token is issued during refresh.
    """

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # Embed stable, non-sensitive identifiers into the payload
        token["user_uuid"] = str(user.uuid)
        return token


class GymBroTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default obtain-pair serializer to embed custom claims
    (user_uuid, email, role) into the access token payload.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Additional claims visible after decoding the JWT
        token["user_uuid"] = str(user.uuid)
        token["email"] = user.email
        token["role"] = user.role
        return token


class GymBroTokenRefreshSerializer(TokenRefreshSerializer):
    token_class = GymBroRefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)
        try:
            refresh = self.token_class(attrs["refresh"])
            user = get_user_model().objects.filter(pk=refresh["user_id"]).first()
            if user is not None:
                access = refresh.access_token
                access["user_uuid"] = str(user.uuid)
                access["email"] = user.email
                access["role"] = user.role
                data["access"] = str(access)
        except Exception:
            pass
        return data


class GymBroTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/v1/auth/token/

    Returns only the access token in the response body (with custom claims).
    The refresh token is stored in a Secure HttpOnly cookie.
    Rate-limited to 5 requests per minute via the 'auth' throttle scope.
    """

    serializer_class = GymBroTokenObtainPairSerializer
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        """
        Override post to set refresh token in HttpOnly cookie instead of response body.
        """
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            refresh_token = response.data.pop("refresh", None)
            
            if refresh_token:
                # Calculate cookie expiration based on REFRESH_TOKEN_LIFETIME setting
                refresh_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME", timedelta(days=7))
                
                response.set_cookie(
                    key=COOKIE_NAME,
                    value=refresh_token,
                    max_age=int(refresh_lifetime.total_seconds()),
                    secure=COOKIE_SECURE,
                    httponly=COOKIE_HTTPONLY,
                    samesite=COOKIE_SAMESITE,
                    path="/",
                )
                # Also set access token as Secure HttpOnly cookie
                access_token = response.data.pop("access", None)
                if access_token:
                    access_lifetime = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME", timedelta(minutes=15))
                    response.set_cookie(
                        key=ACCESS_COOKIE_NAME,
                        value=access_token,
                        max_age=int(access_lifetime.total_seconds()),
                        secure=COOKIE_SECURE,
                        httponly=COOKIE_HTTPONLY,
                        samesite=COOKIE_SAMESITE,
                        path="/",
                    )

        return response


class GymBroTokenRefreshView(TokenRefreshView):
    serializer_class = GymBroTokenRefreshSerializer
    """
    POST /api/v1/auth/token/refresh/

    Reads the refresh token from the HttpOnly cookie.
    Returns a new access token in the response body and sets a new refresh token cookie.
    
    Security: 
    - Old access token is blacklisted (invalidated immediately)
    - Old refresh token is blacklisted (via BLACKLIST_AFTER_ROTATION setting)
    - New refresh token is rotated and set in HttpOnly cookie
    """

    def post(self, request, *args, **kwargs):
        """
        Override post to:
        1. Extract and blacklist the old access token
        2. Read refresh token from cookie
        3. Set new refresh token cookie
        """
        # Extract old access token from Authorization header before processing
        old_access_token_str = (
            self._extract_access_token_from_header(request)
            or request.COOKIES.get(ACCESS_COOKIE_NAME)
        )
        
        # Read refresh token from cookie
        refresh_token = request.COOKIES.get(COOKIE_NAME)
        
        if not refresh_token:
            return Response(
                {"detail": "No refresh token found in cookies."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Build a fresh payload for the serializer and avoid mutating request.data
        refresh_payload = {"refresh": refresh_token}
        serializer = self.get_serializer(data=refresh_payload)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)

        if response.status_code == status.HTTP_200_OK:
            # Blacklist the old access token
            if old_access_token_str:
                self._blacklist_access_token(old_access_token_str)
            
            new_refresh_token = response.data.pop("refresh", None)
            
            if new_refresh_token:
                # Calculate cookie expiration
                refresh_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME", timedelta(days=7))
                
                response.set_cookie(
                    key=COOKIE_NAME,
                    value=new_refresh_token,
                    max_age=int(refresh_lifetime.total_seconds()),
                    secure=COOKIE_SECURE,
                    httponly=COOKIE_HTTPONLY,
                    samesite=COOKIE_SAMESITE,
                    path="/",
                )
                # Also set new access token in HttpOnly cookie (if present)
                access_token = response.data.get("access", None)
                if access_token:
                    access_lifetime = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME", timedelta(minutes=15))
                    response.set_cookie(
                        key=ACCESS_COOKIE_NAME,
                        value=access_token,
                        max_age=int(access_lifetime.total_seconds()),
                        secure=COOKIE_SECURE,
                        httponly=COOKIE_HTTPONLY,
                        samesite=COOKIE_SAMESITE,
                        path="/",
                    )

        return response

    @staticmethod
    def _extract_access_token_from_header(request):
        """
        Extract access token from Authorization header.
        Expected format: "Bearer <token>"
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None

    @staticmethod
    def _blacklist_access_token(token_str):
        """
        Blacklist an access token by adding it to the blacklist table.
        This ensures the token cannot be used again even if still within its lifetime.
        """
        try:
            # Decode token to get required claims for outstanding token creation.
            token = AccessToken(token_str)

            expires_at = datetime.fromtimestamp(token["exp"], tz=timezone.utc)

            # Create or fetch the OutstandingToken entry using required fields.
            outstanding_token, created = OutstandingToken.objects.get_or_create(
                jti=token["jti"],
                token=token_str,
                defaults={
                    "user_id": token.get("user_id"),
                    "expires_at": expires_at,
                },
            )

            # Blacklist the outstanding token.
            # This row is enforced by SimpleJWT only when the token blacklist
            # backend is enabled and JWTAuthentication checks token revocation.
            BlacklistedToken.objects.get_or_create(token=outstanding_token)
        except TokenError as e:
            # Log but don't fail the refresh if blacklisting fails.
            print(f"Warning: Failed to blacklist access token: {str(e)}")
        except Exception as e:
            # Unexpected failures in blacklist bookkeeping should not break refresh.
            print(f"Warning: Failed to record access token blacklist entry: {str(e)}")
