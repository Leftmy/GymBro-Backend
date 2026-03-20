from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import UserRegisterSerializer, UserSerializer
from .services import UserService
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

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