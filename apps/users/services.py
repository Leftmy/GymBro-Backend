from .models import User, UserRole

class UserService:
    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Returns a single user or raises 404 error."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
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