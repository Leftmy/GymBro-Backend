from .models import User
from .validator import UserValidator

class UserService:
    @staticmethod
    def create_user(*, username, email, password):
        UserValidator.validate_registration_data({
            "username": username,
            "email": email,
            "password": password,
        })
        user = User.objects.create_user(username=username, email=email, password=password)
        return user
    
    @staticmethod
    def get_user_by_username(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
    @staticmethod
    def update_user(user, **kwargs):
        for attr, value in kwargs.items():
            setattr(user, attr, value)
        user.save()
        return user
    
    @staticmethod
    def delete_user(user):
        try:
            user.delete()
        except Exception as e:
            raise ValueError(f"Error deleting user: {str(e)}")