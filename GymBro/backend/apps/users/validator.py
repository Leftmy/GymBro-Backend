class UserValidator:
    @staticmethod
    def validate_registration_data(data):
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"{field} is required for registration.")
            
    @staticmethod
    def validate_login_data(data):
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"{field} is required for login.")