from django.contrib.auth import get_user_model
from django.urls import reverse
from django.template.loader import render_to_string

from rest_framework import generics, authentication, permissions
from rest_framework.generics import DestroyAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view

from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    SubscribeSerializer,
    UnSubscribeSerializer,
    VerifyEmailRequestSerializer,
)

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination

import logging
logger = logging.getLogger(__name__)


User = get_user_model()

class UserPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "page_number": self.page.number,  # Add this line
                "results": data,
            }
        )


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        email = request.data.get('email')
        if email:
            existing_users = User.objects.filter(email=email)
            if existing_users.exists():
                user = existing_users.first()
                if len(user.password):
                    return Response({'email': ['user with this email already exists.']}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Update the existing user
                    serializer = self.get_serializer(user, data=request.data)
                    if serializer.is_valid():
                        serializer.save()  # This will now call the update method of the serializer
                        headers = self.get_success_headers(serializer.data)
                        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                # No existing user, proceed with creation
                if serializer.is_valid():
                    serializer.save()
                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'email': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)


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

# class VerifyEmailView(APIView):
    
#     def get(self, request, uidb64, token):
#         try:
#             # Decode the uid
#             uid = urlsafe_base64_decode(uidb64).decode()
#             user = User.objects.get(pk=uid)

#             # Check if the token is valid
#             token_generator = PasswordResetTokenGenerator()
#             if token_generator.check_token(user, token):
#                 # Verify the user's email
#                 user.email_confirmed = True
#                 user.save()
#                 return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             # Handle exceptions
#             return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = []
    serializer_class = PasswordResetRequestSerializer


    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()

            if user is None:
                return Response({"error": "No user associated with this email address."}, status=status.HTTP_400_BAD_REQUEST)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create reset link
            # reset_link = request.build_absolute_uri(
            #     reverse('accounts:password-reset-confirm', args=[uid, token])
            # )
            # Create reset link
            reset_link = f"http://localhost:3000/reset-password/{uid}/{token}"

            # Send email
            # subject = "Password Reset Requested"
            # message = f"Please follow this link to reset your password: {reset_link}"
            # # from_email = None  # Use the DEFAULT_FROM_EMAIL from settings
            # from_email = settings.EMAIL_FROM
            # # from_email = '0eltech0@gmail.com'
            # send_mail(subject, message, from_email, [user.email])

            subject = "Password Reset Requested"
            message = render_to_string('email.html', {
                'user': user,
                'content': f"Please follow this link to reset your password: {reset_link}"
            })
            from_email = settings.EMAIL_FROM
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

class SubscribeView(APIView):
    permission_classes = []
    serializer_class = SubscribeSerializer

    def post(self, request, *args, **kwargs):
        serializer = SubscribeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                # Check if user already exists
                user = User.objects.get(email=email)
                if user.is_subscribed:
                    return Response({"message": "This email is already subscribed."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                # If user does not exist, create a new inactive user
                user = User.objects.create(email=email, is_active=False)
                # Send an email to set a password, confirm the email, etc.

            # Subscribe the user
            user.is_subscribed = True
            user.save()
            # Send a subscription confirmation email here
            # You can send a welcome email here.
            return Response({"message": "You've been subscribed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnSubscribeView(APIView):
    permission_classes = []
    serializer_class = SubscribeSerializer

    def post(self, request, *args, **kwargs):
        serializer = UnSubscribeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                # Check if user already exists
                user = User.objects.get(email=email)

                if user.is_subscribed:
                    user.is_subscribed = False
                    user.save()
                    return Response({"message": "You've successfully unsubscribed from our website."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"message": "You have not subscribed before!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailRequestView(generics.GenericAPIView):
    permission_classes = []
    serializer_class = VerifyEmailRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Create verification link
                verification_link = f"http://localhost:3000/verify-email/{uid}/{token}"

                # Send email
                # subject = "Email Verification Requested"
                # message = f"Please follow this link to verify your email: {verification_link}"
                # # from_email = None  # Use the DEFAULT_FROM_EMAIL from settings
                # from_email = settings.EMAIL_FROM
                # send_mail(subject, message, from_email, [user.email])

                subject = "Email Verification Requested"
                message = render_to_string('email.html', {
                    'user': user,
                    'content': f"Please follow this link to verify your email: {verification_link}"
                })
                from_email = settings.EMAIL_FROM
                send_mail(subject, message, from_email, [user.email])

        # Always return the same message whether the user exists or not
        # to prevent data leakage
        return Response({"message": "If an account with the email exists, a verification link has been sent."}, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):

    def post(self, request, uidb64, token):
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



class CheckAdminView(APIView):
    """
    Check if the current logged-in user is an admin.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.is_staff:
            # If the user is an admin (staff), return a success response
            return Response({'is_admin': True})
        else:
            # If the user is not an admin, return a failure response
            return Response({'is_admin': False})
        
        
class UserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    pagination_class = UserPagination
    queryset = User.objects.all()

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
# class DeleteUserView(DestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminUser] 


# class RetrieveUserView(generics.RetrieveAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserRoleView(views.APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
