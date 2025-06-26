from rest_framework import serializers
from .models import CustomUser
from .enums import RoleChoices
from django.contrib.auth.tokens import default_token_generator

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'role']
        read_only_fields = ['role']

    def validate_role(self, value):
        user = self.context['request'].user

        if user.is_authenticated and user.role == RoleChoices.MANAGER and value != RoleChoices.EMPLOYEE:
            raise serializers.ValidationError("Managers can only create employees.")
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance

class AdminUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'role']


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.IntegerField()
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)

    def validate(self, attrs):
        try:
            user = CustomUser.objects.get(pk=attrs['uid'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid user ID.")
        
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired token.")
        
        attrs['user'] = user
        return attrs
