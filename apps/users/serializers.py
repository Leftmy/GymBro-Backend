from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Паролі не збігаються."})
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'uuid', 'username', 'email', 'role', 'created_at')
        read_only_fields = fields