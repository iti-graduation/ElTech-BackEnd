from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer
)

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail

from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return the authenticated user"""

        return self.request.user

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            # Decode the uid
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            # Check if the token is valid
            token_generator = PasswordResetTokenGenerator()
            if token_generator.check_token(user, token):
                # Verify the user's email
                user.email_confirmed = True
                user.save()
                return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle exceptions
            return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = []
    serializer_class = PasswordResetRequestSerializer


    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Create reset link
                reset_link = request.build_absolute_uri(
                    reverse('accounts:password-reset-confirm', args=[uid, token])
                )

                # Send email
                subject = "Password Reset Requested"
                message = f"Please follow this link to reset your password: {reset_link}"
                from_email = None  # Use the DEFAULT_FROM_EMAIL from settings
                send_mail(subject, message, from_email, [user.email])

        # Always return the same message whether the user exists or not
        # to prevent data leakage
        return Response({"message": "If an account with the email exists, a password reset link has been sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            # Check the token and save the new password
            if default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)