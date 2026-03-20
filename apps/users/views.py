from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import (
    UserUpdateSerializer,
    UserRegisterSerializer, 
    UserLoginSerializer,
    UserSerializer,
)
from .services import UserService
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        validated_data.pop('password_confirm', None)
        
        user = UserService.create_user(**validated_data)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: dict},
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_data = UserService.authenticate_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        response_data = {
            "access": auth_data['access'],
            "refresh": auth_data['refresh'],
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        """Retrieve current user's data."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request):
        """Update current user's profile."""
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.update_user(
            user_id=request.user.id, 
            **serializer.validated_data
        )
        
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request):
        """Delete current user's profile."""
        UserService.delete_user(request.user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)