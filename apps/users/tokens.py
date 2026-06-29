"""
Custom JWT token classes and serializers for GymBro.

Embeds additional claims (user_uuid, email, role) into the access token
so that downstream services can identify the user without an extra DB lookup.
"""

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class GymBroRefreshToken(RefreshToken):
    """
    Custom RefreshToken that injects extra claims into the access token.
    Used by the service layer when generating tokens manually.
    """

    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # Embed stable, non-sensitive identifiers into the payload
        token.access_token["user_uuid"] = str(user.uuid)
        token.access_token["email"] = user.email
        token.access_token["role"] = user.role
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


class GymBroTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/v1/auth/token/

    Returns access + refresh JWT pair with custom claims embedded.
    Rate-limited to 5 requests per minute via the 'auth' throttle scope.
    """

    serializer_class = GymBroTokenObtainPairSerializer
    # Override the default throttle classes to apply the 'auth' scope
    throttle_scope = "auth"
