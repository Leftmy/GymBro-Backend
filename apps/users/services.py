from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from .models import User, UserRole
from django.db import transaction

class UserService:
    @staticmethod
    def get_user_by_name(username: str) -> User:
        """Returns a single user or raises 404 error."""
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Returns a single user or raises 404 error."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def search_users(
        query: str,
        limit: int = 10,
        offset: int = 0,
    ):

        query = query.lower().strip()

        return (
            User.objects
            .filter(
                username_normalized__istartswith=query
            )
            .exclude(is_active=False)
            .order_by("username_normalized")
            [offset:offset + limit]
        )


    @staticmethod
    @transaction.atomic
    def create_user(*, username: str, email: str, password: str, role: str = UserRole.CLIENT) -> User:
        if role == UserRole.ADMIN:
            return User.objects.create_superuser(
                username=username, 
                email=email, 
                password=password,
                role=UserRole.ADMIN
            )
        
        return User.objects.create_user(
            username=username, 
            email=email, 
            password=password, 
            role=role
        )
    
    @staticmethod
    @transaction.atomic
    def update_user(user_id: int, **data) -> User | None:
        """
        Updates a specific user.
        """
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        
        password = data.pop('password', None)
        if password:
            user.set_password(password)

        for attr, value in data.items():
            setattr(user, attr, value)
                
        user.save()
        return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        user = UserService.get_user_by_id(user_id)
        if user:
            user.delete()
            return True
        return False


    @staticmethod
    def authenticate_user(email, password):
        user = authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed("Wrong email or password")
        
        if not user.is_active:
            raise AuthenticationFailed("User's unactive")

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }