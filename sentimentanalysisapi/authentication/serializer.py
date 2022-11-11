from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric character')

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['token']

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=68, read_only=True)
    access_token = serializers.CharField(max_length=68, read_only=True)

    class Meta:
        model = User
        fields = ['id','email','password','username','refresh_token', 'access_token']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid creditials, please try again')

        if not user.is_active:
            raise AuthenticationFailed('Account disabled, please contact admin')

        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified. Please verified first')

        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'refresh_token': user.tokens(),
            'access_token': user.accessToken()

        }
        return super().validate(attrs)

