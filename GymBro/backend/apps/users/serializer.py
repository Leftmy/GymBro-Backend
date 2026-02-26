class UserSerializer:
    def __init__(self, user):
        self.user = user

    def data(self):
        return {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "is_admin": self.user.is_admin,
            "created_at": self.user.created_at,
            "updated_at": self.user.updated_at,
            "is_active": self.user.is_active,
            "is_staff": self.user.is_staff,
        }