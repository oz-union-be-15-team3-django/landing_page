from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """회원가입 Serializer"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """프로필 조회 Serializer"""
    joined_at = serializers.DateTimeField(source='date_joined', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'joined_at')
        read_only_fields = ('id', 'username', 'email', 'joined_at')


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """프로필 수정 Serializer"""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ProfileUpdateResponseSerializer(serializers.ModelSerializer):
    """프로필 수정 응답 Serializer"""
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'updated_at')
        read_only_fields = ('id', 'username', 'email', 'updated_at')


class UserSignupResponseSerializer(serializers.ModelSerializer):
    """회원가입 응답 Serializer"""
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'created_at')
        read_only_fields = ('id', 'username', 'email', 'created_at')

