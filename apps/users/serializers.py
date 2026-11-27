from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_('A user with this email already exists.'))
        return value

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_('A user with this username already exists.'))
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': _('Passwords do not match.')})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email']

    def validate_username(self, value):
        value = value.strip()
        exists = (
            User.objects
            .filter(username__iexact=value)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if exists:
            raise serializers.ValidationError(_('A user with this username already exists.'))
        return value
