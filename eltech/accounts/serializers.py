from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = ('email', 'password', 'mobile_phone', 'profile_picture',
                  'birth_date', 'country', 'is_subscribed', 'first_name', 'last_name',
                  'facebook_profile', 'instagram_profile', 'twitter_profile')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""

        user = User.objects.create_user(**validated_data)
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create verification link
        verify_link = reverse('accounts:verify-email', args=[uid, token])

        # Email content
        subject = 'Verify your account'
        message = f'Follow this link to verify your account: {verify_link}'
        from_email = '0eltech0@gmail.com'
        recipient_list = [user.email]

        # Send email
        send_mail(subject, message, from_email, recipient_list)

        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token serializer"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={
            'input_type': 'password'
        },
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""

        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The two passwords do not match.")
        return data

class SubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value, is_subscribed=True).exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return value

class UnSubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value, is_subscribed=False).exists():
            raise serializers.ValidationError("This email is not subscribed.")
        return value